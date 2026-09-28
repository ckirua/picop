# picoipc SPSC backend optimization study

Charter for improving Python `picoipc` throughput via native bindings while keeping a fast merge gate.

## Methods (one branch per approach)

| Branch | Backend | `PICOIPC_BACKEND` |
|--------|---------|-----------------|
| `opt/ctypes` | ctypes → `libsmh_q.so` | `ctypes` |
| `opt/pybind11` | pybind11 extension | `pybind11` |
| `opt/cython` | Cython wrapper | `cython` |
| `main` (baseline) | pybind11 extension | `pybind11` |

Branch naming: `opt/<method>` off `main`. Do not stack multiple binding approaches on one branch.

## Gate workflow

```bash
git checkout -b opt/ctypes
# implement binding + set PICOIPC_BACKEND for local runs
./bench/run_gate.sh
```

`run_gate.sh` builds C++ (Release), runs `bench/harness.py` with `bench/config_smoke.yaml`, and compares the pybind11 output to `artifacts/baseline.json`.

### Smoke gate rules (`config_smoke.yaml`)

| Check | Rule |
|-------|------|
| Correctness | All steps in `correctness` pass (`cpp_roundtrip`, `cpp_stress`, `py_roundtrip`, `py_cpp_xlang`) |
| Throughput | `sequential_msgs_per_sec_64b` >= `baseline x throughput_multiplier` (default 1.25) |
| Wall time | Harness completes within `max_wall_s` (default 90) |
| Regression | C++ cross-language roundtrip must pass |

Optional deep profile: `bench/config_full.yaml` (not run on every PR).

### Artifacts

- `artifacts/baseline.json` — committed pybind11 production baseline.
- `artifacts/bench_<git_sha>.json` — per-run pybind11 harness output (not committed on opt branches unless intentionally promoting a new baseline).
- `artifacts/bench_pure.json` — ignored pure-Python correctness-smoke output.

Record branch outcomes in `research/runs/<branch>.md` (setup, numbers, verdict). Append promoted merges to `research/OPTIMIZATION_LOG.md`.

## Promotion policy

After a branch merges to `main`:

1. Set the default backend in `src/picoipc/__init__.py` to the winner.
2. Intentionally refresh `artifacts/baseline.json` from the new default through the documented promotion workflow.
3. Add a row to `research/OPTIMIZATION_LOG.md`.

Do **not** merge if the gate fails, C++ cross-lang breaks, or deps are heavy without proportional gain (e.g. Cython vs pybind11). Never update a baseline through `RECORD_BASELINE` or ordinary CI.

## CI

PRs run the repository-root `.github/workflows/picoipc-smoke.yml` with two required obligations:

1. `./bench/run_gate.sh` builds the production pybind11 backend, runs CTest and configured correctness checks, then compares throughput against the committed pybind11 baseline.
2. The explicit `PICOIPC_BACKEND=pure` harness run is a required correctness smoke with no throughput comparison.
