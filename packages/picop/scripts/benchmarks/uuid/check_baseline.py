#!/usr/bin/env python3
"""Check UUID benchmark medians against measured absolute baselines."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
import gzip
import json
import math
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

_BASELINE = Path(__file__).resolve().parent / "results" / "baseline.json"
_DEFAULT_MAX_REGRESSION_PCT = Decimal("25")


def _percentage(value: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError(f"invalid percentage: {value!r}") from exc
    if not parsed.is_finite() or parsed < 0:
        raise argparse.ArgumentTypeError("percentage must be finite and non-negative")
    return parsed


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare measured UUID medians with absolute cypy baselines."
    )
    parser.add_argument("result", type=Path, help="JSON produced by bench.py")
    parser.add_argument(
        "--max-regression-pct",
        type=_percentage,
        default=_DEFAULT_MAX_REGRESSION_PCT,
        metavar="N",
        help="largest permitted slowdown percentage (default: 25)",
    )
    return parser


def _load_json(path: Path) -> dict[str, Any]:
    try:
        if path.suffix == ".gz":
            with gzip.open(path, "rt", encoding="utf-8") as stream:
                data = json.load(stream)
        else:
            with path.open(encoding="utf-8") as stream:
                data = json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _positive_decimal(value: Any, label: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f"{label} must be a positive number")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{label} must be a positive finite number")
    try:
        parsed = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{label} must be a positive number") from exc
    if not parsed.is_finite() or parsed <= 0:
        raise ValueError(f"{label} must be a positive finite number")
    return parsed


def _gated_baselines(data: dict[str, Any]) -> dict[str, Decimal]:
    operations = data.get("operations")
    if not isinstance(operations, dict):
        raise ValueError("baseline has no operations object")

    gated: dict[str, Decimal] = {}
    for name, entry in operations.items():
        if not isinstance(name, str) or not isinstance(entry, dict):
            raise ValueError("baseline operation entries must be objects")
        if entry.get("gate") is not True:
            continue
        gated[name] = _positive_decimal(
            entry.get("median_ns"), f"baseline {name}.median_ns"
        )
    if not gated:
        raise ValueError("baseline has no gated operations")
    return gated


def _validate_result(
    data: dict[str, Any], gated_operations: Mapping[str, Decimal]
) -> None:
    schema_version = data.get("schema_version")
    if isinstance(schema_version, bool) or schema_version != 1:
        raise ValueError("result schema_version must be 1")
    if data.get("suite") != "cypy.uuid":
        raise ValueError("result suite must be 'cypy.uuid'")

    operations = data.get("operations")
    if not isinstance(operations, Mapping):
        raise ValueError("result operations must be an object")
    for operation in gated_operations:
        entry = operations.get(operation)
        if isinstance(entry, Mapping) and entry.get("unit") != "nanosecond":
            raise ValueError(f"result {operation}.unit must be 'nanosecond'")


def _result_median(data: dict[str, Any], operation: str) -> Decimal:
    operations = data.get("operations")
    if not isinstance(operations, dict):
        raise KeyError(operation)
    entry = operations.get(operation)
    if not isinstance(entry, dict) or "median_ns" not in entry:
        raise KeyError(operation)
    return _positive_decimal(entry["median_ns"], f"result {operation}.median_ns")


def _decimal_text(value: Decimal, *, signed: bool = False) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if signed and value >= 0:
        return f"+{text}"
    return text


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        baseline = _gated_baselines(_load_json(_BASELINE))
        result = _load_json(args.result)
        _validate_result(result, baseline)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    failed = False
    for operation, expected in baseline.items():
        try:
            measured = _result_median(result, operation)
        except KeyError:
            print(f"{operation}: missing result median", file=sys.stderr)
            failed = True
            continue
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            failed = True
            continue

        delta_ns = measured - expected
        delta_pct = delta_ns * Decimal(100) / expected
        limit = expected * (Decimal(1) + args.max_regression_pct / Decimal(100))
        passed = measured <= limit
        status = "PASS" if passed else "FAIL"
        print(
            f"{operation}: baseline={_decimal_text(expected)} ns "
            f"result={_decimal_text(measured)} ns "
            f"delta={_decimal_text(delta_ns, signed=True)} ns "
            f"({_decimal_text(delta_pct, signed=True)}%) "
            f"limit={_decimal_text(args.max_regression_pct)}% {status}"
        )
        failed |= not passed

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
