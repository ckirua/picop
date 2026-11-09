#!/usr/bin/env python3
"""Check the measured Tier A ratios against the table in ``docs/PERF_PARITY.md``.

Reads one or more ``perf_parity_report.py --json`` dumps (the CI job collects one
per interpreter: 3.14, 3.15, 3.14t, 3.15t) and reports drift.

Tier A ratios jitter by several percent between runs - a helper whose *minimum*
case sits at 1.01x one run and 1.04x the next - so the gates use margins and only
fire on contradictions that survive every dump:

* a helper documented as always slower whose **mean** ratio is ``<= 0.90`` in
  every dump is stale: the wrapper is no longer losing to the builtin;
* a helper absent from the table that averages ``>= 1.25`` in every dump is a
  real loss that needs a doc row and a stub note;
* anything smaller is reported, not failed.

Run locally after regenerating:

    python scripts/perf_parity_report.py --json > /tmp/parity-3.15.json
    python scripts/perf_parity_drift.py --dir /tmp --glob 'parity-*.json'
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from perf_parity_report import public_names  # noqa: E402

DOC_HEADING = "## Always slower from pure Python"
ROW_RE = re.compile(r"^\|\s*`([A-Za-z_][A-Za-z0-9_]*)`\s*\|\s*[^|]+\|\s*([0-9.]+)x\s*\|")
STALE_BELOW = 0.90
NEW_ABOVE = 1.25
INFO_DRIFT = 0.20
GIL_TO_FREE = 0.30


def documented_rows(doc: Path) -> dict[str, float]:
    text = doc.read_text(encoding="utf-8")
    if DOC_HEADING not in text:
        raise SystemExit(f"{doc}: missing '{DOC_HEADING}' section")
    section = text.split(DOC_HEADING, 1)[1].split("\n## ", 1)[0]
    rows: dict[str, float] = {}
    for line in section.splitlines():
        match = ROW_RE.match(line)
        if match:
            rows[match.group(1)] = float(match.group(2))
    return rows


def mean(cases: list[tuple[float, str]]) -> float:
    return sum(ratio for ratio, _ in cases) / len(cases)


def is_free_threaded(label: str) -> bool:
    return label.endswith("t")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", type=Path, default=Path("parity"), help="directory holding the JSON dumps")
    ap.add_argument("--glob", default="parity-*.json", help="glob for the dumps")
    ap.add_argument("--doc", type=Path, default=Path("docs/PERF_PARITY.md"))
    args = ap.parse_args()

    dumps = sorted(args.dir.glob(args.glob))
    if not dumps:
        raise SystemExit(f"no dumps matched {args.dir}/{args.glob}")

    labels: dict[str, dict[str, float]] = {}
    failures: list[str] = []
    for path in dumps:
        data = json.loads(path.read_text(encoding="utf-8"))
        label = path.stem.removeprefix("parity-")
        failures.extend(data.get("failures", []))
        pub = public_names()
        labels[label] = {
            name: mean(cases)
            for name, cases in data["ratios"].items()
            if name in pub
        }
    if failures:
        print("bench failures:", file=sys.stderr)
        for line in failures:
            print("  " + line, file=sys.stderr)

    doc_rows = documented_rows(args.doc)
    helpers = sorted(set(doc_rows) | {name for means in labels.values() for name in means})

    problems: list[str] = []
    for name in helpers:
        measured = [means[name] for means in labels.values() if name in means]
        if name in doc_rows:
            if not measured:
                problems.append(f"`{name}` is in the table but no dump measured it")
            elif max(measured) <= STALE_BELOW:
                problems.append(
                    f"`{name}` is documented at {doc_rows[name]:.2f}x but averages "
                    f"{min(measured):.2f}-{max(measured):.2f}x in every dump"
                )
        elif len(measured) == len(labels) and min(measured) >= NEW_ABOVE:
            problems.append(
                f"`{name}` averages {min(measured):.2f}-{max(measured):.2f}x in every dump "
                "but is not in the table"
            )

    reference = next((label for label in sorted(labels) if not is_free_threaded(label)), sorted(labels)[0])
    movers = sorted(
        (
            (abs(ratio - doc_rows[name]), name, doc_rows[name], ratio)
            for name, ratio in labels[reference].items()
            if name in doc_rows and abs(ratio - doc_rows[name]) >= INFO_DRIFT
        ),
        reverse=True,
    )
    penalty: list[tuple[float, str, float, float]] = []
    for name in doc_rows:
        ratios = [(label, labels[label][name]) for label in labels if name in labels[label]]
        gil = [ratio for label, ratio in ratios if not is_free_threaded(label)]
        ft = [ratio for label, ratio in ratios if is_free_threaded(label)]
        if gil and ft and max(ft) - min(gil) >= GIL_TO_FREE:
            penalty.append((max(ft) - min(gil), name, min(gil), max(ft)))
    penalty.sort(reverse=True)

    print(f"dumps: {', '.join(sorted(labels))}")
    print(f"documented helpers: {len(doc_rows)}")
    if movers:
        print(f"movements of {INFO_DRIFT:.2f}x or more against {reference} (informational):")
        for _, name, documented, measured in movers:
            print(f"  `{name}`: {documented:.2f}x -> {measured:.2f}x")
    if penalty:
        print(f"helpers costing {GIL_TO_FREE:.2f}x more with the GIL off:")
        for _, name, gil_ratio, ft_ratio in penalty:
            print(f"  `{name}`: {gil_ratio:.2f}x (GIL) -> {ft_ratio:.2f}x (no GIL)")
    if problems:
        print("\ndrift that needs a doc update:")
        for line in problems:
            print("  " + line)
        print(
            "regenerate from the measured dumps: python scripts/perf_parity_report.py "
            f"--from-json parity/{reference}.json --update-doc --sync-stubs"
        )
        return 1
    print("docs/PERF_PARITY.md matches the measured ratios")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
