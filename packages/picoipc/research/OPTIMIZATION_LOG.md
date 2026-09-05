# Optimization Log

| Date | Branch | Backend | Sequential msgs/s (64B) | Speedup vs pure_python | Gate | Merged |
|------|--------|---------|---------------------------|------------------------|------|--------|
| 2026-08-23 | main (baseline) | pure_python | 60,668 | 1.00x | PASS | yes |
| 2026-08-23 | opt/ctypes | ctypes | 288,932 | 4.76x | PASS | yes |
| 2026-08-23 | opt/pybind11 | pybind11 | 2,049,091 | 33.78x | PASS | yes |
| 2026-08-23 | opt/cython | cython | 60,330 | 0.99x | FAIL | no |

Default backend after study: **pybind11** (with ctypes → pure fallback).

Production migration (2026-08-23): the Python package backend selector, `bench/run_gate.sh`, and `artifacts/baseline.json` use pybind11. Run `./bench/run_all_backends.sh` to benchmark every backend.
| 2026-08-23 | opt/py-zero-copy | pybind11 | ~1,770k | ~0.87x vs main | FAIL | no |
| 2026-08-23 | opt/py-publish-fastpath | pybind11 | ~1,770k | ~0.87x vs main | FAIL | no |

Baseline refreshed on main (9188b5b): ~2.03M msgs/s smoke sequential 64B.
| 2026-08-23 | opt/cpp-spin-env | pybind11 | 2,086,113 (smoke) / 2,100,690 (full) | 1.03x vs baseline | PASS | yes |
| 2026-08-23 | opt/py-publish-only | pybind11 | ~2,110,753 (median) | 1.04x vs pre-merge baseline | PASS | yes |
| 2026-08-23 | opt/march-native-bench | pybind11 | C++ ~6.25M (±0.1%) | py seq unchanged | PASS | yes |
| 2026-08-23 | py314-baseline | pybind11 | ~2.09M | 1.03x | PASS | yes |
| 2026-08-23 | opt/py314-freethreading | pybind11 | GIL seq ~2.26M | threaded 50x (1.25M vs 25k) | PASS | yes |
