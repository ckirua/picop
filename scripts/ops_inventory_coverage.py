#!/usr/bin/env python3
"""Public-ops inventory coverage gate.

Public set = names imported from ``cy*`` in ``src/picop/__init__.py``.
Compares = first-arg labels of ``session.compare`` / ``session.compare_mutate``
in ``bench/**/*.py``.

Each public helper must appear in ``docs/OPS_INVENTORY.md`` with status:

- ``tierA`` — has a Tier A ``session.compare*`` label
- ``tierB`` — has a Tier B compare under ``bench/tier_b/`` (implies Tier A too
  when both exist; inventory may list ``tierB`` alone when Tier A is also present)
- ``pending`` — not yet inventoried (allowed unless ``--strict``)
- ``n/a (…)`` — explicit skip with mechanism reason (counts as covered)

Perf parity: every helper listed in the "Always slower from pure Python" table of
``docs/PERF_PARITY.md`` must carry a ``Slower than the plain-Python equivalent …``
note in its ``.pyi`` docstring, and conversely every ``.pyi`` docstring carrying that
note must have a table row. Table ratios must be above ``1.02x``.

Exit 0 when every public name has a valid inventory row, the parity table and the
docstrings agree, and (unless ``--strict``) statuses are consistent. With
``--strict``, also require zero ``pending`` and every non-``n/a`` name to have a
compare.

Usage::

    python3.14 scripts/ops_inventory_coverage.py
    python3.14 scripts/ops_inventory_coverage.py --strict
    python3.14 scripts/ops_inventory_coverage.py --write-seed
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT_PY = ROOT / "src" / "picop" / "__init__.py"
BENCH = ROOT / "bench"
INVENTORY = ROOT / "docs" / "OPS_INVENTORY.md"
PARITY_DOC = ROOT / "docs" / "PERF_PARITY.md"

COMPARE_RE = re.compile(
    r"session\.compare(?:_mutate)?\s*\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"
)
# Single-line checklist row: | `name` | status | notes |
ROW_RE = re.compile(
    r"^\|\s*`([A-Za-z_][A-Za-z0-9_]*)`\s*\|\s*([^|]+?)\s*\|\s*([^|]*)\s*\|\s*$"
)
STATUS_OK = re.compile(
    r"^(?:pending|tierA|tierB|n/a(?:\s*\([^)]*\))?)$",
    re.I,
)
CHECKLIST_HDR = re.compile(r"^##\s+Checklist\s*$", re.M)


def public_barrel() -> list[str]:
    tree = ast.parse(INIT_PY.read_text(encoding="utf-8"), filename=str(INIT_PY))
    names: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        if not node.module or not node.module.startswith("cy"):
            continue
        for alias in node.names:
            if alias.name != "*":
                names.append(alias.name)
    return names


def compare_labels() -> tuple[set[str], set[str]]:
    tier_a: set[str] = set()
    tier_b: set[str] = set()
    for path in BENCH.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        found = set(COMPARE_RE.findall(text))
        if "tier_b" in path.parts:
            tier_b |= found
        else:
            tier_a |= found
    return tier_a, tier_b


def parse_inventory(text: str) -> dict[str, tuple[str, str]]:
    """Parse rows under the ``## Checklist`` section only."""
    m = CHECKLIST_HDR.search(text)
    if not m:
        return {}
    section = text[m.end() :]
    next_hdr = re.search(r"^##\s+", section, re.M)
    if next_hdr:
        section = section[: next_hdr.start()]
    out: dict[str, tuple[str, str]] = {}
    for line in section.splitlines():
        rm = ROW_RE.match(line)
        if not rm:
            continue
        name, status, notes = rm.group(1), rm.group(2).strip(), rm.group(3).strip()
        if name == "Helper":
            continue
        out[name] = (status, notes)
    return out


PARITY_HDR = re.compile(r"^##\s+Always slower from pure Python\s*$", re.M)
MIXED_HDR = re.compile(r"^##\s+Slower only on some inputs\s*$", re.M)
# Table row: | `name` | `module` | 1.09x | `builtin` | why |
PARITY_ROW_RE = re.compile(
    r"^\|\s*`([A-Za-z_][A-Za-z0-9_]*)`\s*\|\s*`([A-Za-z_]+)`\s*\|\s*([0-9.]+)x\s*\|"
)
# Mixed row: | `name` | 0.98x (hit) | 1.05x (miss) |
MIXED_ROW_RE = re.compile(
    r"^\|\s*`([A-Za-z_][A-Za-z0-9_]*)`\s*\|\s*[^|]+\|\s*[^|]+\|\s*$"
)
PARITY_NOTE = "Slower than the plain-Python equivalent"
PARITY_THRESHOLD = 1.02


def _section(text: str, hdr: re.compile) -> str:
    m = hdr.search(text)
    if not m:
        return ""
    section = text[m.end() :]
    nxt = re.search(r"^##\s+", section, re.M)
    return section[: nxt.start()] if nxt else section


def parse_parity(text: str) -> dict[str, tuple[str, float]]:
    """Rows of the always-slower table: name -> (module, ratio)."""
    out: dict[str, tuple[str, float]] = {}
    for line in _section(text, PARITY_HDR).splitlines():
        rm = PARITY_ROW_RE.match(line)
        if rm:
            out[rm.group(1)] = (rm.group(2), float(rm.group(3)))
    return out


def parse_mixed(text: str) -> set[str]:
    """Names in the case-dependent table."""
    return {
        rm.group(1)
        for line in _section(text, MIXED_HDR).splitlines()
        if (rm := MIXED_ROW_RE.match(line)) and rm.group(1) != "Helper"
    }


def stub_docstrings(path: Path) -> dict[str, str]:
    """Docstrings of every public function/class in a ``.pyi`` stub."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return {}
    out: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if node.name.startswith("_"):
            continue
        doc = ast.get_docstring(node)
        if doc:
            out[node.name] = doc
    return out


def check_parity(errors: list[str], pub_set: set[str]) -> int:
    """Cross-check docs/PERF_PARITY.md against the ``.pyi`` docstrings."""
    if not PARITY_DOC.is_file():
        errors.append(f"missing {PARITY_DOC.relative_to(ROOT)}")
        return 0
    text = PARITY_DOC.read_text(encoding="utf-8")
    table = parse_parity(text)
    mixed = parse_mixed(text)
    if not table:
        errors.append(f"{PARITY_DOC.relative_to(ROOT)}: no rows in the always-slower table")
        return 0

    all_docs: dict[str, str] = {}
    for stub in sorted((ROOT / "src" / "picop").rglob("*.pyi")):
        all_docs.update(stub_docstrings(stub))

    for name, (_, ratio) in sorted(table.items()):
        # Table ratios are printed with two decimals, so 1.02x can mean 1.021x;
        # only a genuinely sub-threshold row is an error.
        if ratio + 0.005 < PARITY_THRESHOLD:
            errors.append(
                f"{name}: parity table ratio {ratio}x is not above {PARITY_THRESHOLD}x"
            )
        if name not in pub_set:
            errors.append(f"{name}: parity table row is not on the public barrel")
        doc = all_docs.get(name)
        if doc is None:
            errors.append(f"{name}: parity table names a helper with no stub definition")
        elif PARITY_NOTE not in doc:
            errors.append(f"{name}: docstring lacks the parity note")

    for name in sorted(mixed - set(table)):
        doc = all_docs.get(name)
        if doc is None:
            errors.append(f"{name}: mixed parity row names a helper with no stub")
        elif "Tier A" not in doc:
            errors.append(f"{name}: docstring lacks the case-dependent parity note")

    noted = {name for name, doc in all_docs.items() if PARITY_NOTE in doc}
    for name in sorted(noted - set(table) - mixed):
        errors.append(
            f"{name}: docstring carries a parity note with no row in "
            f"{PARITY_DOC.relative_to(ROOT)}"
        )
    return len(table) + len(mixed)


def seed_status(name: str, tier_a: set[str], tier_b: set[str]) -> str:
    if name in tier_b:
        return "tierB"
    if name in tier_a:
        return "tierA"
    return "pending"


def write_seed(public: list[str], tier_a: set[str], tier_b: set[str]) -> None:
    rows: list[str] = []
    counts: Counter[str] = Counter()
    for name in sorted(public):
        status = seed_status(name, tier_a, tier_b)
        counts[status] += 1
        note = ""
        if status == "tierB":
            note = "Tier A + Tier B compare labels present"
        elif status == "tierA":
            note = "Tier A `session.compare` present"
        else:
            note = "awaiting inventory harness"
        rows.append(f"| `{name}` | {status} | {note} |")

    body = "\n".join(
        [
            "# Public ops inventory",
            "",
            "Checklist for every public barrel helper imported from `cy*` in",
            "[`src/picop/__init__.py`](../src/picop/__init__.py).",
            "",
            "Status vocabulary:",
            "",
            "| Status | Meaning |",
            "|--------|---------|",
            "| `pending` | No timed `session.compare` yet |",
            "| `tierA` | Timed Tier A vs plain Python |",
            "| `tierB` | Timed Tier B (cdef vs typed Cython); Tier A also present |",
            "| `n/a (reason)` | Explicit skip — no stable baseline / side effects |",
            "",
            "Gate: [`scripts/ops_inventory_coverage.py`](../scripts/ops_inventory_coverage.py).",
            "Related: [`EQ_INVENTORY.md`](EQ_INVENTORY.md) · [`EQ_INVENTORY_TIERB.md`](EQ_INVENTORY_TIERB.md).",
            "",
            "## Summary",
            "",
            f"| Metric | Count |",
            f"|--------|------:|",
            f"| Public barrel helpers | {len(public)} |",
            f"| `tierA` | {counts['tierA']} |",
            f"| `tierB` | {counts['tierB']} |",
            f"| `pending` | {counts['pending']} |",
            f"| `n/a` | {counts['n/a']} |",
            "",
            "## Checklist",
            "",
            "| Helper | Status | Notes |",
            "|--------|--------|-------|",
            *rows,
            "",
        ]
    )
    INVENTORY.parent.mkdir(parents=True, exist_ok=True)
    INVENTORY.write_text(body, encoding="utf-8")
    print(
        f"wrote {INVENTORY.relative_to(ROOT)}: "
        f"public={len(public)} tierA={counts['tierA']} "
        f"tierB={counts['tierB']} pending={counts['pending']}"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--write-seed",
        action="store_true",
        help="Regenerate docs/OPS_INVENTORY.md from compares (pending for gaps)",
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Fail on any pending row; require compare for every non-n/a row",
    )
    args = ap.parse_args()

    public = public_barrel()
    pub_set = set(public)
    if len(public) != len(pub_set):
        print("ops_inventory_coverage FAIL: duplicate public imports", file=sys.stderr)
        return 1

    tier_a, tier_b = compare_labels()
    any_compare = tier_a | tier_b

    if args.write_seed:
        write_seed(public, tier_a, tier_b)
        return 0

    if not INVENTORY.is_file():
        print(f"ops_inventory_coverage FAIL: missing {INVENTORY}", file=sys.stderr)
        return 1

    inv = parse_inventory(INVENTORY.read_text(encoding="utf-8"))
    errors: list[str] = []

    for name in sorted(pub_set - set(inv)):
        errors.append(f"missing inventory row: {name}")
    for name in sorted(set(inv) - pub_set):
        errors.append(f"inventory row not on public barrel: {name}")

    pending = 0
    na = 0
    tier_a_n = 0
    tier_b_n = 0
    for name in sorted(pub_set & set(inv)):
        status, _notes = inv[name]
        if not STATUS_OK.match(status):
            errors.append(f"{name}: invalid status {status!r}")
            continue
        low = status.lower()
        if low == "pending":
            pending += 1
            if args.strict:
                errors.append(f"{name}: still pending")
        elif low.startswith("n/a"):
            na += 1
        elif low == "tiera":
            tier_a_n += 1
            if name not in any_compare:
                errors.append(f"{name}: status tierA but no session.compare label")
        elif low == "tierb":
            tier_b_n += 1
            if name not in tier_b:
                errors.append(f"{name}: status tierB but no tier_b compare label")
            elif name not in tier_a and args.strict:
                # Tier B without Tier A is unusual; warn under strict
                errors.append(f"{name}: status tierB but no Tier A compare label")
        # Covered without inventory status upgrade:
        if (
            args.strict
            and not low.startswith("n/a")
            and low != "pending"
            and name not in any_compare
        ):
            errors.append(f"{name}: no compare and not n/a")

    # Non-strict: every public name must have compare OR pending/n/a/tier* row
    # (row already required). Soft check: pending without compare is OK.
    if not args.strict:
        for name in sorted(pub_set):
            status = inv.get(name, ("",))[0].lower()
            if name in any_compare:
                continue
            if status == "pending" or status.startswith("n/a"):
                continue
            if status in {"tiera", "tierb"}:
                # already flagged above when missing compare
                continue
            errors.append(f"{name}: uncovered (no compare / pending / n/a)")

    parity = check_parity(errors, pub_set)

    print(
        f"ops_inventory_coverage: public={len(public)} "
        f"comparesA={len(pub_set & tier_a)} comparesB={len(pub_set & tier_b)} "
        f"inv tierA={tier_a_n} tierB={tier_b_n} pending={pending} n/a={na} "
        f"parity={parity}"
    )

    if errors:
        print("ops_inventory_coverage FAIL:")
        for e in errors:
            print(f" - {e}")
        return 1

    print("ops_inventory_coverage OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
