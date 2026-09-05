# opt/cpp-spin-env — env-configurable spin-before-futex

## Change
Replace hardcoded `kSpinIters=2000` and 1 ms futex slice in `Ring::wait_readable()` with env vars matching `ull::SpscRing` semantics:

| Env | Default | Purpose |
|-----|---------|---------|
| `SMH_Q_SHM_SPIN_ITERS` | 2000 | Spin iterations before futex wait |
| `SMH_Q_SHM_WAIT_MS` | 1 | Futex wait slice (ms) |

## Gate (smoke, `bench/config_smoke.yaml`)
- **VERDICT: PASS** vs `artifacts/baseline.json` (pybind11, same impl)
- Correctness: **PASS** (cpp roundtrip/stress, py roundtrip, py↔cpp xlang)
- Sequential (pybind11, 64B): **2,086,113 msgs/s** (baseline 2,028,993 → **1.03x**)
- C++ sequential: **6,379,138 msgs/s** (baseline 6,371,204 → 1.00x)

Defaults unchanged; env tuning is opt-in at runtime.

## Threaded (`bench/config_full.yaml`, 100k msgs)
| Variant | Sequential msgs/s | Threaded msgs/s |
|---------|-------------------|-----------------|
| `main` baseline (memo prior run) | ~1,819,360 | ~24,934 |
| `opt/cpp-spin-env` (defaults) | **2,100,690** | **24,524** |

Threaded delta vs main: **~1.6%** (within noise; no regression).

## `bench_futex` env line
```
Env: SMH_Q_SHM_SPIN_ITERS=(unset) SMH_Q_SHM_WAIT_MS=(unset) (defaults 2000, 1)
```

## Files
- `native/src/ring.cpp` — `getenv_int`, `shm_spin_iters`, `shm_wait_slice_ms`
- `benchmarks/native/bench_futex.cpp` — print active env
- `README.md` — relation-to-ull env tuning note

## Merge
Merged to `main` (bcb4c7d) after smoke gate PASS (correctness + seq ≥ baseline × 1.0).
