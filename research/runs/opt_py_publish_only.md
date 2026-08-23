# opt/py-publish-only — publish fastpath, main consume drain

## Summary

Branch `opt/py-publish-only` ports **only** the publish-side fastpath from `opt/py-publish-fastpath` (`ee35a67`): `try_publish_length`, `publish(length)`, harness publish via `claim`/`publish` or `try_publish_length`. The timed drain loop keeps **`try_consume()`** (not `try_consume_into`).

## Gate results (smoke, pybind11, 3 runs)

| Run | sequential_msgs_per_sec_64b |
|-----|----------------------------|
| 1 | 2,068,501 |
| 2 | 2,163,096 |
| 3 | 2,110,753 |

| Metric | Main baseline (`artifacts/baseline.json`) | Candidate median | Ratio |
|--------|-------------------------------------------|------------------|-------|
| sequential_msgs_per_sec_64b | 2,028,993 | **2,110,753** | **1.04x** |
| correctness | PASS | PASS | — |
| wall_s | 0.038 | 0.037–0.038 | PASS |

**Verdict: PASS** — median >= baseline × 1.0.

## vs opt/py-publish-fastpath

That branch coupled publish fastpath with `try_consume_into` drain (~0.87x vs main). Publish-only + `try_consume()` drain recovers throughput to ~main+4%.

## Changes

- **C++** (`ring.hpp`, `ring.cpp`): public `claim()`, `publish(length)`, `publish_payload`, `try_publish_length`, `has_claim()`.
- **pybind11** (`pybind_module.cpp`): `claim`, `publish`, `try_consume_into`, buffer `try_publish` (APIs exposed; gate drain unchanged).
- **Harness** (`bench/harness.py`): `_make_publish_fn()` for zero-fill `publish(length)`; drain stays `while ring.try_consume() is None`.

## Merge

Merged to `main` (PASS).
