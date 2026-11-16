#!/usr/bin/env python3
"""Delta between CPython public headers and a committed baseline.

``docs/INVENTORY_315.md`` is a set-diff of public declarations between the
previous minor release and the target release. This script regenerates that
diff: every symbol the target interpreter adds must be either linked by picop,
listed in ``scripts/header_ledger.json`` with a mechanism reason, or triaged —
no silent skips.

Run in the target interpreter (CI uses 3.15)::

    python scripts/header_delta.py --baseline scripts/header_baseline_314.json --fail-on-unaccounted
    python scripts/header_delta.py --write-baseline scripts/header_baseline_314.json   # regenerate baseline

Symbols the baseline declared and the target no longer does are reported as
``removed``; picop references to those are flagged so the version guards can be
checked.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import sysconfig
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUFFIXES = {".pyx", ".pxd", ".py", ".h", ".pyi"}
SKIP_HEADERS = {"pymac.h", "pydtrace.h"}
DECL = re.compile(
    r"PyAPI_FUNC\s*\([^)]*\)\s*([A-Za-z_]\w*)\s*\(|PyAPI_DATA\s*\([^)]*\)\s*([A-Za-z_]\w*)",
)
MACRO = re.compile(r"^\s*#\s*define\s+(Py[A-Za-z_]\w*)\b", re.M)


def header_files(root: Path) -> list[Path]:
    out = []
    for path in sorted(root.glob("*.h")):
        if path.name not in SKIP_HEADERS:
            out.append(path)
    cpython = root / "cpython"
    if cpython.is_dir():
        for path in sorted(cpython.glob("*.h")):
            if path.name not in SKIP_HEADERS:
                out.append(path)
    return out


def declarations(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for path in header_files(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in DECL.finditer(text):
            # A Py_DEPRECATED annotation may sit on the line(s) before the declaration.
            line_start = text.rfind("\n", 0, match.start()) + 1
            prior_start = text.rfind("\n", 0, max(0, line_start - 1)) + 1
            if "Py_DEPRECATED" in text[prior_start:line_start]:
                continue
            symbol = match.group(1) or match.group(2)
            out.setdefault(symbol, path.relative_to(root).as_posix())
    return out


def reference_text() -> str:
    parts: list[str] = []
    for base in (ROOT / "src/picop", ROOT / "examples/cimport_ext"):
        if base.is_dir():
            for path in base.rglob("*"):
                if path.is_file() and path.suffix in SUFFIXES:
                    parts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def ledger_entry(ledger: dict, symbol: str):
    entry = ledger.get(symbol)
    if entry is not None:
        return entry
    for key, value in ledger.items():
        if key.endswith("*") and symbol.startswith(key[:-1]):
            return value
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--baseline", type=Path, help="JSON baseline (list or {\"symbols\": [...]}) to diff against")
    ap.add_argument("--write-baseline", type=Path, help="write the current symbol set to this path and exit")
    ap.add_argument("--include", type=Path, help="header root to scan instead of the running interpreter's (e.g. an unpacked CPython source tree)")
    ap.add_argument("--ledger", type=Path, default=Path(__file__).with_name("header_ledger.json"))
    ap.add_argument("--json", action="store_true", help="emit the full classification as JSON")
    ap.add_argument("--fail-on-unaccounted", action="store_true", help="exit 1 when an added symbol is neither linked nor ledger-listed")
    args = ap.parse_args()

    include = args.include if args.include else Path(sysconfig.get_path("include"))
    if not include.is_dir():
        print(f"header root not found: {include}", file=sys.stderr)
        return 1
    symbols = declarations(include)
    if args.write_baseline:
        args.write_baseline.write_text(json.dumps({"symbols": sorted(symbols)}, indent=1) + "\n", encoding="utf-8")
        print(f"baseline written: {args.write_baseline} ({len(symbols)} public declarations)")
        return 0

    ledger = json.loads(args.ledger.read_text(encoding="utf-8")) if args.ledger.exists() else {}
    reftext = reference_text()

    if args.baseline:
        data = json.loads(args.baseline.read_text(encoding="utf-8"))
        base = set(data["symbols"] if isinstance(data, dict) else data)
    else:
        base = set()

    added = sorted(set(symbols) - base)
    removed = sorted(base - set(symbols))

    classification: dict[str, dict] = {}
    unaccounted: list[str] = []
    for symbol in added:
        entry = ledger_entry(ledger, symbol)
        linked = bool(re.search(r"\b" + re.escape(symbol) + r"\b", reftext))
        classification[symbol] = {"header": symbols[symbol], "linked": linked, "ledger": entry}
        if not linked and entry is None:
            unaccounted.append(symbol)

    stale = [symbol for symbol in removed if re.search(r"\b" + re.escape(symbol) + r"\b", reftext)]
    summary = (
        f"public={len(symbols)} baseline={len(base)} added={len(added)} "
        f"added_linked={sum(item['linked'] for item in classification.values())} "
        f"added_ledger={sum(item['ledger'] is not None for item in classification.values())} "
        f"unaccounted={len(unaccounted)} removed={len(removed)} removed_referenced={len(stale)}"
    )
    if args.json:
        print(json.dumps({"added": classification, "removed": removed, "removed_referenced": stale}, indent=2, sort_keys=True))
    else:
        print(summary)
        for symbol in unaccounted:
            print(f"unaccounted: {symbol} ({classification[symbol]['header']})")
        for symbol in stale:
            print(f"removed-but-referenced: {symbol}")
    return 1 if args.fail_on_unaccounted and unaccounted else 0


if __name__ == "__main__":
    raise SystemExit(main())
