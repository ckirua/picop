# opt/ctypes — ctypes binding to libsmh_q.so

## Setup
- `native/bindings/c_api.cpp` + `native/include/smh_q/c_api.h`
- `python/smh_q/_ctypes_ring.py` via ctypes
- `SMH_Q_BACKEND=ctypes`

## Gate results (smoke)

| Metric | pure_python baseline | ctypes |
|--------|---------------------|--------|
| sequential_msgs_per_sec_64b | 60,668 | 288,932 |
| speedup | 1.00x | **4.76x** |
| correctness | PASS | PASS |
| wall_s | — | 0.055 |

## Verdict
**PASS** — merged to main.
