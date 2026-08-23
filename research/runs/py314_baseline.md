# py314-baseline — Python 3.14 requirement bump

## Changes
- `requires-python = ">=3.14"` in `python/pyproject.toml`
- README: Python 3.14+ required; note `python3.14` vs `python3.14t`
- CI smoke workflow: `actions/setup-python` with Python 3.14
- `bench/run_gate.sh`: version assert `sys.version_info >= (3, 14)` before harness

## Environment
- Python: 3.14.4 (`python3`)
- Backend: pybind11 (default; `SMH_Q_BACKEND` unset)

## Gate results (smoke)
| Metric | Baseline | Candidate | Ratio |
|--------|----------|-----------|-------|
| sequential_msgs_per_sec_64b | 2,028,993 | 2,055,187 | 1.01x |
| cpp_sequential_msgs_per_sec_64b | 6,371,204 | 6,387,817 | 1.00x |

- correctness: PASS
- wall time: PASS (0.04s / 90.0s)
- throughput: PASS

**VERDICT: PASS**

## Merge
Merged to `main`; `artifacts/baseline.json` refreshed from gate candidate.
