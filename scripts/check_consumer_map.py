#!/usr/bin/env python3
"""Validate source-derived coverage and integrity of the use-cypy consumer catalog."""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = ("Symbol", "Kind", "Access", "Decision", "Expression or use", "Contract", "Python evidence", "Cython evidence")
KINDS = {"function", "class", "method", "property", "type", "constant"}
ACCESS = {"python", "cimport", "both"}
DECISIONS = {"candidate", "specialized", "not-replacement", "companion", "legacy"}
ROW = re.compile(r'^\|\s*<a id="([A-Za-z_][A-Za-z0-9_-]*)"></a>`([^`]+)`\s*\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|\s*$')


def _load_sources(root: Path):
    script = ROOT / "scripts" / "consumer_map_sources.py"
    if not script.is_file():
        raise FileNotFoundError(f"missing {script}")
    if str(script.parent) not in sys.path:
        sys.path.insert(0, str(script.parent))
    spec = importlib.util.spec_from_file_location("consumer_map_sources", script)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {script}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def _error(errors: list[str], path: Path, line: int, message: str) -> None:
    errors.append(f"{path.as_posix()}:{line}: {message}")


def _validate(root: Path) -> tuple[list[str], Counter[str], Counter[str], dict[str, int]]:
    errors: list[str] = []
    source_module = _load_sources(root)
    expected = source_module.enumerate_sources(root)
    source_totals = source_module.source_counts(root, expected)
    mapdir = root / ".cursor/skills/use-cypy/maps"
    files = sorted(mapdir.glob("*.md")) if mapdir.is_dir() else []
    actual: dict[str, tuple[dict[str, str], Path, int]] = {}
    module_files = {p.stem: p for p in files}
    if not files:
        errors.append(f"{mapdir}: no module map files")
    cats: Counter[str] = Counter()
    states: Counter[str] = Counter()
    for path in files:
        lines = path.read_text(encoding="utf-8").splitlines()
        header_seen = False
        for n, line in enumerate(lines, 1):
            if not line.startswith("|"):
                for target in re.findall(r"\]\(([^)]+)\)", line):
                    _check_link(root, path, n, target, errors)
            if line.startswith("| Symbol |"):
                header_seen = True
                if tuple(x.strip() for x in line.strip("|").split("|")) != COLUMNS:
                    _error(errors, path, n, "invalid table columns")
                continue
            if not line.startswith("|") or line.startswith("|---"):
                continue
            match = ROW.match(line)
            if not match:
                _error(errors, path, n, f"malformed catalog row (escape literal pipes as &#124;): {line}")
                continue
            anchor, key, *cells = [x.strip() for x in match.groups()]
            if "*" in key or "," in key or " " in key:
                _error(errors, path, n, f"invalid or grouped symbol key {key!r}")
            if key in actual:
                _error(errors, path, n, f"duplicate key {key}")
                continue
            if key not in expected:
                _error(errors, path, n, f"unknown key {key}")
                continue
            meta = expected[key]
            kind, access, decision, expr, contract, py_ev, cy_ev = cells
            local = key.removeprefix("picop.uuid._uuid.") if path.stem == "uuid" else key.removeprefix(f"picop.{path.stem}.")
            want_anchor = local.replace(".", "-")
            if anchor != want_anchor:
                _error(errors, path, n, f"{key}: anchor must be {want_anchor!r}")
            if path.stem != key.split(".")[1]:
                _error(errors, path, n, f"{key}: row is in wrong module map")
            if kind not in KINDS or kind != meta["kind"]:
                _error(errors, path, n, f"{key}: kind {kind!r} does not match source kind {meta['kind']!r}")
            if access not in ACCESS or access != meta["access"]:
                _error(errors, path, n, f"{key}: access {access!r} does not match source access {meta['access']!r}")
            if decision not in DECISIONS:
                _error(errors, path, n, f"{key}: invalid decision {decision!r}")
            for label, value in zip(COLUMNS[4:], (expr, contract, py_ev, cy_ev)):
                if not value:
                    _error(errors, path, n, f"{key}: empty required {label} cell")
            for label, value in (("Python", py_ev), ("Cython", cy_ev)):
                if not re.match(r"^(recorded|harness-only|not-measured|not-applicable):\s*\S", value):
                    _error(errors, path, n, f"{key}: invalid {label} evidence state")
                else:
                    states[value.split(":", 1)[0]] += 1
                if value.startswith(("harness-only:", "not-measured:")) and re.search(r"\b(?:\d+(?:\.\d+)?x|\d+%)\b", value):
                    _error(errors, path, n, f"{key}: unmeasured evidence contains a speed result")
                for target in re.findall(r"\]\(([^)]+)\)", value):
                    _check_link(root, path, n, target, errors)
            for target in re.findall(r"\]\(([^)]+)\)", expr + " " + contract):
                _check_link(root, path, n, target, errors)
            actual[key] = (meta, path, n)
            cats[meta["kind"]] += 1
            if decision in ("companion", "legacy"):
                cats[decision] += 1
            if "skip-python" in py_ev.lower():
                cats["skip-python"] += 1
            if "case-dependent" in (py_ev + " " + cy_ev).lower():
                cats["case-dependent"] += 1
        if not header_seen:
            _error(errors, path, 1, "missing table header")
    for key in sorted(set(expected) - set(actual)):
        errors.append(f"missing catalog row {key}")
    _check_index(root, module_files, errors)
    parity_doc = root / "docs/PERF_PARITY.md"
    if parity_doc.is_file():
        text = parity_doc.read_text(encoding="utf-8")
        helper_path = root / "scripts" / "ops_inventory_coverage.py"
        if not helper_path.is_file():
            helper_path = ROOT / "scripts" / "ops_inventory_coverage.py"
        helper_spec = importlib.util.spec_from_file_location("ops_inventory_coverage", helper_path)
        if helper_spec is None or helper_spec.loader is None:
            errors.append(f"cannot load {helper_path}")
            parity, mixed = {}, set()
        else:
            helper = importlib.util.module_from_spec(helper_spec)
            helper_spec.loader.exec_module(helper)
            parity = helper.parse_parity(text)
            mixed = helper.parse_mixed(text)
        for name in parity:
            matches = [k for k in expected if k.rsplit(".", 1)[-1] == name]
            for key in matches:
                row = next((p for k, (_, p, _) in actual.items() if k == key), None)
                if row:
                    line = next((ln for ln in row.read_text(encoding="utf-8").splitlines() if f"`{key}`" in ln), "")
                    parsed = ROW.match(line)
                    if not parsed or "skip-python" not in parsed.group(8).lower():
                        errors.append(f"{row}: {key} must mark parity loser skip-python")
        for name in mixed:
            for key in expected:
                if key.rsplit(".", 1)[-1] == name and key in actual:
                    row_path = actual[key][1]
                    line = next((ln for ln in row_path.read_text(encoding="utf-8").splitlines() if f"`{key}`" in ln), "")
                    parsed = ROW.match(line)
                    if not parsed or "case-dependent" not in parsed.group(8).lower():
                        errors.append(f"{row_path}: {key} must mark mixed result case-dependent")
    cats["rows"] = len(expected)
    return errors, cats, states, source_totals


def _check_link(root: Path, source: Path, line: int, target: str, errors: list[str]) -> None:
    if "://" in target or target.startswith("mailto:"):
        return
    dest, _, fragment = target.partition("#")
    path = (source.parent / dest).resolve() if dest else source
    try:
        path.relative_to(root.resolve())
    except ValueError:
        _error(errors, source, line, f"link escapes selected root: {target}")
        return
    if not path.exists():
        _error(errors, source, line, f"missing link target {target}")
        return
    if fragment and path.suffix.lower() == ".md":
        text = path.read_text(encoding="utf-8")
        anchors = set(re.findall(r'<a id="([^"]+)"', text))
        anchors.update(re.sub(r"[^a-z0-9 -]", "", h.lower()).strip().replace(" ", "-") for h in re.findall(r"^#+\s+(.+)$", text, re.M))
        if fragment not in anchors:
            _error(errors, source, line, f"missing fragment #{fragment} in {path.relative_to(root)}")


def _check_index(root: Path, module_files: dict[str, Path], errors: list[str]) -> None:
    index = root / ".cursor/skills/use-cypy/catalog.md"
    if not index.is_file():
        errors.append(f"missing {index.relative_to(root)}")
        return
    text = index.read_text(encoding="utf-8")
    module_section = text.split("## Module maps", 1)[-1].split("\n## ", 1)[0]
    entries = re.findall(r"^\|\s*[^|]+\|\s*\[[^]]+\]\(([^)]+)\)\s*\|", module_section, re.M)
    counts = Counter(entries)
    for module in module_files:
        target = f"maps/{module}.md"
        if counts[target] != 1:
            errors.append(f"{index.relative_to(root)}: module {module} must appear exactly once (found {counts[target]})")
    for target in entries:
        _check_link(root, index, 1, target, errors)
    for path in (index, root / ".cursor/skills/use-cypy/SKILL.md"):
        if path.is_file():
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for target in re.findall(r"\]\(([^)]+)\)", line):
                    _check_link(root, path, n, target, errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        errors, counts, states, source_totals = _validate(root)
    except Exception as exc:
        print(f"consumer-map: {exc}")
        return 1
    for error in errors:
        print(f"ERROR: {error}")
    labels = {"python_barrel": "Python barrel", "supplemental": "Additional Cython callables", "uuid": "UUID", "class_members": "Class members", "companions": "Companion types/constants"}
    for category in ("python_barrel", "supplemental", "uuid", "class_members", "companions"):
        print(f"  {labels[category]}: {source_totals.get(category, 0)}")
    for category in ("function", "method", "property", "class", "type", "constant", "legacy", "skip-python", "case-dependent"):
        print(f"  {category}: {counts[category]}")
    print("Evidence cells: " + ", ".join(f"{key}={states[key]}" for key in ("recorded", "harness-only", "not-measured", "not-applicable")))
    if errors:
        return 1
    print(f"Consumer map valid: {counts['rows']} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
