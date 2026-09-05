# opt/py314-freethreading — Python 3.14 free-threading

## Environment

| Item | Value |
|------|-------|
| `python3.14` | `python3.14` (GIL build) — `gil_enabled: True` |
| `python3.14t` | `python3.14t` (free-threaded build) — `gil_enabled: False` |
| Config | `bench/config_full.yaml` |
| Extension | pybind11 `_native` built per-interpreter (`-DPython_EXECUTABLE=…`) with `py::mod_gil_not_used()` |

Build (both interpreters):

```bash
cmake -S cpp -B cpp/build-gil -DCMAKE_BUILD_TYPE=Release -DSMH_Q_BUILD_PYTHON=ON \
  -DPYBIND11_FINDPYTHON=ON -DPython_EXECUTABLE=$(which python3.14)
cmake --build cpp/build-gil -j
cp cpp/build-gil/_native.cpython-314-x86_64-linux-gnu.so python/smh_q/

cmake -S cpp -B cpp/build-ft -DCMAKE_BUILD_TYPE=Release -DSMH_Q_BUILD_PYTHON=ON \
  -DPYBIND11_FINDPYTHON=ON -DPython_EXECUTABLE=$(which python3.14t)
cmake --build cpp/build-ft -j
cp cpp/build-ft/_native.cpython-314t-x86_64-linux-gnu.so python/smh_q/
```

Run: `bench/run_freethreading.sh` or set `SMH_Q_FREETHREADING=1` to invoke `python3.14t` only.

## Results (`threaded_msgs_per_sec_64b`, 100k msgs, 64B payload)

| Build | `gil_enabled` | sequential (64B) | threaded (64B) |
|-------|---------------|------------------|----------------|
| python3.14 (GIL) | `true` | 2,257,216 | **24,943** |
| python3.14t (no-GIL) | `false` | 2,020,497 | **1,248,256** |

- Threaded speedup (no-GIL / GIL): **50.0×** (gate: ≥1.25×) ✓
- GIL sequential vs main smoke baseline (~2.03M): no regression ✓
- no-GIL sequential vs GIL sequential: −10.5% (free-threaded build; GIL path unchanged)

## Verdict

**PASS** — free-threaded Python removes the GIL bottleneck on the threaded harness (producer thread + consumer thread). Merge to `main`.

Artifacts: `artifacts/bench_py314_gil.json`, `artifacts/bench_py314_nogil.json`
