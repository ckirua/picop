# smh_q / picosmh optimization study

Charter for improving Python `smh_q` throughput via native bindings while keeping a fast merge gate.

## Methods (one branch per approach)

| Branch | Backend | `SMH_Q_BACKEND` |
|--------|---------|-----------------|
| `opt/ctypes` | ctypes → `libsmh_q.so` | `ctypes` |
| `opt/pybind11` | pybind11 extension | `pybind11` |
| `opt/cython` | Cython wrapper | `cython` |
| `main` (baseline) | pure Python ring | `pure` |

Branch naming: `opt/<method>` off `main`. Do not stack multiple binding approaches on one branch.

## Gate workflow

```bash
git checkout -b opt/ctypes
# implement binding + set SMH_Q_BACKEND for local runs
./bench/run_gate.sh
```

`run_gate.sh` builds C++ (Release), runs `bench/harness.py` with `bench/config_smoke.yaml`, compares output to `artifacts/baseline.json`.

### Smoke gate rules (`config_smoke.yaml`)

| Check | Rule |
|-------|------|
| Correctness | All steps in `correctness` pass (`cpp_roundtrip`, `cpp_stress`, `py_roundtrip`, `py_cpp_xlang`) |
| Throughput | `sequential_msgs_per_sec_64b` >= `baseline x throughput_multiplier` (default 1.25) |
| Wall time | Harness completes within `max_wall_s` (default 90) |
| Regression | C++ cross-language roundtrip must pass |

Optional deep profile: `bench/config_full.yaml` (not run on every PR).

### Artifacts

- `artifacts/baseline.json` — committed on `main`; pure-Python reference numbers.
- `artifacts/bench_<git_sha>.json` — per-run harness output (not committed on opt branches unless refreshing baseline after merge).

Record branch outcomes in `research/runs/<branch>.md` (setup, numbers, verdict). Append promoted merges to `research/OPTIMIZATION_LOG.md`.

## Promotion policy

After a branch merges to `main`:

1. Set default backend in `python/smh_q/__init__.py` to the winner.
2. Refresh `artifacts/baseline.json` from the new default.
3. Add a row to `research/OPTIMIZATION_LOG.md`.

Do **not** merge if the gate fails, C++ cross-lang breaks, or deps are heavy without proportional gain (e.g. Cython vs pybind11).

## CI

PRs run `.github/workflows/smoke.yml`: cmake build + `./bench/run_gate.sh` (~2 min).
