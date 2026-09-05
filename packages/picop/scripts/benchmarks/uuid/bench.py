#!/usr/bin/env python3
"""Run reproducible microbenchmarks for :mod:`cypy.uuid`."""

from __future__ import annotations

import gzip
import json
import os
import platform
import statistics
import sys
from datetime import UTC, datetime
from tempfile import TemporaryDirectory
from pathlib import Path
from typing import Any
from uuid import UUID as StdlibUUID

import pyperf

from cypy.uuid import UUID, uuid4, uuid4_bytes

_CANONICAL = "123e4567-e89b-42d3-a456-426614174000"
_RAW = bytes.fromhex("123e4567e89b42d3a456426614174000")
_VALUE = UUID(_RAW)
_STDLIB_VALUE = StdlibUUID(bytes=_RAW)

# Prime the two lazy caches before timing their steady-state access.
_VALUE.int
hash(_VALUE)


def _gil_enabled() -> bool | None:
    probe = getattr(sys, "_is_gil_enabled", None)
    return probe() if probe is not None else None


def _cpu_metadata(pyperf_metadata: dict[str, Any]) -> dict[str, Any]:
    affinity: list[int] | None = None
    get_affinity = getattr(os, "sched_getaffinity", None)
    if get_affinity is not None:
        try:
            affinity = sorted(get_affinity(0))
        except OSError:
            pass

    return {
        "model": pyperf_metadata.get("cpu_model_name") or platform.processor() or None,
        "logical_count": os.cpu_count(),
        "affinity": affinity,
    }


def _runtime_metadata() -> dict[str, Any]:
    return {
        "implementation": platform.python_implementation(),
        "version": platform.python_version(),
        "executable": sys.executable,
        "compiler": platform.python_compiler(),
        "gil_enabled": _gil_enabled(),
    }


def _operation_result(benchmark: Any) -> dict[str, Any]:
    samples_ns = [value * 1_000_000_000 for value in benchmark.get_values()]
    return {
        "unit": "nanosecond",
        "sample_count": len(samples_ns),
        "samples_ns": samples_ns,
        "median_ns": statistics.median(samples_ns),
        "mean_ns": statistics.fmean(samples_ns),
    }


def _write_json(path: Path, data: dict[str, Any]) -> None:
    text = json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if path.suffix == ".gz":
        with gzip.open(path, "wt", encoding="utf-8") as stream:
            stream.write(text)
    else:
        path.write_text(text, encoding="utf-8")


def _run_benchmarks(runner: pyperf.Runner) -> None:
    runner.timeit("uuid4", "uuid4()", globals={"uuid4": uuid4})
    runner.timeit(
        "uuid4_bytes", "uuid4_bytes()", globals={"uuid4_bytes": uuid4_bytes}
    )
    runner.timeit(
        "UUID_from_str",
        "UUID(CANONICAL)",
        globals={"UUID": UUID, "CANONICAL": _CANONICAL},
    )
    runner.timeit(
        "UUID_from_bytes", "UUID(RAW)", globals={"UUID": UUID, "RAW": _RAW}
    )
    runner.timeit("str", "str(value)", globals={"value": _VALUE})
    runner.timeit("hex", "value.hex", globals={"value": _VALUE})
    runner.timeit("int_cached", "value.int", globals={"value": _VALUE})
    runner.timeit("hash_cached", "hash(value)", globals={"value": _VALUE})
    runner.timeit(
        "stdlib_equality",
        "value == stdlib_value",
        globals={"value": _VALUE, "stdlib_value": _STDLIB_VALUE},
    )


def main() -> None:
    runner = pyperf.Runner(
        values=3,
        processes=20,
        warmups=1,
        metadata={"benchmark_suite": "cypy.uuid"},
    )
    args = runner.parse_args()

    # pyperf re-executes this module with --worker and --pipe. Workers must
    # register the same tasks in the same order, but only the selected task is
    # timed and written to the manager pipe.
    if args.worker:
        _run_benchmarks(runner)
        return

    if not args.output:
        runner.argparser.error("--output PATH is required")
    if args.append or args.pipe is not None:
        runner.argparser.error("--append and --pipe are not supported by this JSON harness")

    custom_output = Path(args.output)
    with TemporaryDirectory(prefix="cypy-uuid-pyperf-") as directory:
        native_output = Path(directory) / "suite.json"
        # Reserve the user-requested path for our stable schema. pyperf writes
        # its native suite to a separate file after each manager task.
        args.output = str(native_output)
        _run_benchmarks(runner)
        with native_output.open(encoding="utf-8") as stream:
            suite = pyperf.BenchmarkSuite.load(stream)

        expected_names = (
            "uuid4",
            "uuid4_bytes",
            "UUID_from_str",
            "UUID_from_bytes",
            "str",
            "hex",
            "int_cached",
            "hash_cached",
            "stdlib_equality",
        )
        actual_names = set(suite.get_benchmark_names())
        missing = [name for name in expected_names if name not in actual_names]
        if missing:
            raise RuntimeError(f"pyperf suite has no result for: {', '.join(missing)}")

        benchmarks = {
            name: suite.get_benchmark(name) for name in expected_names
        }
        common_metadata = next(iter(benchmarks.values())).get_metadata()
        result = {
            "schema_version": 1,
            "suite": "cypy.uuid",
            "generated_at": datetime.now(UTC).isoformat(),
            "runtime": _runtime_metadata(),
            "system": {
                "platform": platform.platform(),
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
            },
            "cpu": _cpu_metadata(common_metadata),
            "pyperf": {
                "version": pyperf.__version__,
                "processes": args.processes,
                "values_per_process": args.values,
                "warmups_per_process": args.warmups,
                "minimum_value_time_seconds": args.min_time,
            },
            "operations": {
                name: _operation_result(benchmark)
                for name, benchmark in benchmarks.items()
            },
        }

    _write_json(custom_output, result)


if __name__ == "__main__":
    main()
