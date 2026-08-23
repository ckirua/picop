# opt/cython — Cython wrapper

## Setup
- `python/smh_q/_cython_ring.pyx` calling `smh_q_ring_*` C API
- Build via `python/setup_cython.py`

## Gate results (smoke)

| Metric | pure_python | cython | pybind11 (ref) |
|--------|-------------|--------|----------------|
| sequential_msgs_per_sec_64b | 60,668 | 60,330 | 2,049,091 |
| speedup vs baseline | 1.00x | 0.99x | 33.78x |
| correctness | PASS | PASS | PASS |
| wall_s | — | 0.131 | 0.038 |

## Verdict
**no merge** — fails 1.25x throughput gate and is not competitive with pybind11 (~34x slower). Extension not shipped on `main`; `SMH_Q_BACKEND=cython` is a stub.
