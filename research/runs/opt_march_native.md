# opt/march-native-bench — `-march=native` for C++ lib + benchmarks

## Change
- CMake option `SMH_Q_NATIVE_ARCH` (default OFF)
- When ON or `SMH_Q_NATIVE_ARCH=1` env: `-march=native` on `smh_q` static lib + benchmark targets only
- pybind11 module, examples, and shared lib unchanged (CI default portable)

## C++ bench_sequential (100k, 64B, Release, same host, 3-run avg)

| Build | msgs/s | vs default |
|-------|--------|------------|
| Default Release | 6258069 | 1.00x |
| SMH_Q_NATIVE_ARCH=1 | 6250702 | 0.999x (-0.1%) |

C++ bump: **-0.1%** on this host (host-specific; marginal on this CPU).

## Gate (smoke, python3.14 GIL, `bench/config_smoke.yaml`)

| Metric | baseline | candidate |
|--------|----------|-----------|
| pybind sequential (64B) | 2,028,993 | 2,104,977 |
| VERDICT | — | **PASS** |

pybind sequential unchanged as expected (binding overhead dominates; no `-march=native` on `_native` module).

## Verdict
**PASS** — opt-in only; default CI build unaffected.
