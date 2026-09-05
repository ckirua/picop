from __future__ import annotations

import importlib.util
from pathlib import Path


COMPARE = Path(__file__).parents[1] / "bench" / "compare.py"
spec = importlib.util.spec_from_file_location("picoipc_compare", COMPARE)
compare = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(compare)


def metrics(impl: str, sequential: float, cpp_sequential: float) -> dict:
    return {
        "impl": impl,
        "sequential_msgs_per_sec_64b": sequential,
        "cpp_sequential_msgs_per_sec_64b": cpp_sequential,
    }


def test_normalized_rate_removes_host_speed_shift_for_same_backend() -> None:
    baseline = metrics("pybind11", 100.0, 1_000.0)
    candidate = metrics("pybind11", 95.0, 950.0)

    assert compare.normalized_rate(baseline, candidate, 95.0) == 100.0


def test_normalized_rate_preserves_backend_comparison() -> None:
    baseline = metrics("pure_python", 100.0, 1_000.0)
    candidate = metrics("pybind11", 95.0, 950.0)

    assert compare.normalized_rate(baseline, candidate, 95.0) == 95.0


def test_normalized_rate_keeps_unexplained_regression() -> None:
    baseline = metrics("pybind11", 100.0, 1_000.0)
    candidate = metrics("pybind11", 85.0, 950.0)

    assert compare.normalized_rate(baseline, candidate, 85.0) < 100.0

def test_same_backend_allows_bounded_residual_variance() -> None:
    baseline = metrics("pybind11", 100.0, 1_000.0)
    candidate = metrics("pybind11", 95.0, 950.0)

    assert compare.required_multiplier(baseline, candidate, 1.25) == 0.90

def test_different_backend_retains_configured_speedup_requirement() -> None:
    baseline = metrics("pure_python", 100.0, 1_000.0)
    candidate = metrics("pybind11", 95.0, 950.0)

    assert compare.required_multiplier(baseline, candidate, 1.25) == 1.25
