# picoipc — Low-Latency Local IPC

Linux-focused IPC primitives for Python and C++. The current implementation is a **single-producer / single-consumer (SPSC)** ring buffer over POSIX shared memory (`shm_open` + `mmap`) with **futex** wakeups.

The ring is a standalone `smh_q` C++ engine with no external gateway, database, or exchange runtime dependencies.

**Linux only.** Requires `shm_open`, `mmap`, and `futex`.

## What is SPSC and why SHM + futex?

| Concept | Meaning |
|---------|---------|
| **SPSC** | One writer, one reader. Sequence counters coordinate access without locks on the hot path. |
| **POSIX SHM** | Named region in `/dev/shm` mapped into two processes — zero-copy IPC. |
| **Futex** | Kernel wait/wake on `write_seq`. Consumer spins briefly, then sleeps until publish. |

## Memory layout

```
offset 0
+--------------------------------------------------------------+
| RingHeader (20 B): magic, schema_id, version,                |
|   slot_count, slot_size, header_bytes                        |
+--------------------------------------------------------------+
| pad to 64 B                                                  |
+--------------------------------------------------------------+
| write_seq u32 @ offset 64 (own cache line)                   |
+--------------------------------------------------------------+
| read_seq u32  @ offset 128 (own cache line)                  |
+--------------------------------------------------------------+
| pad to 64 B                                                  |
+--------------------------------------------------------------+
| slot[i]: length u32 | reserved u32 | payload[...]            |
+--------------------------------------------------------------+
```

Default magic: `0x534D4851` (`"SMHQ"`).

## Package layout

```
picoipc/
  README.md  LICENSE
  native/include/smh_q/ring.hpp  native/src/ring.cpp  native/CMakeLists.txt
  examples/cpp/{roundtrip,producer,consumer,stress}.cpp
  benchmarks/cpp/{bench_throughput,bench_sequential,bench_futex}.cpp
  pyproject.toml  src/picoipc/{__init__,ring}.py
  examples/python/{roundtrip,producer,consumer,stress}.py
  benchmarks/python/bench_throughput.py
```

## Build (C++)

```bash
cmake -S native -B build/native -DCMAKE_BUILD_TYPE=Release
cmake --build build/native
```

## Bundled C++ API (`smh_q::Ring`)

- `Ring::Config` — `name`, `slot_count`, `slot_size`, `schema_id`, `version`, `magic`
- `Ring(cfg, create)` — create or attach POSIX shm
- `try_publish(span<const byte>)` — non-blocking; false if full
- `try_consume()` — `optional<vector<byte>>`
- `wait_readable(chrono::milliseconds)` — spin + futex wait
- `Ring::unlink(name)`

## Python

**Python 3.14+ required** (`requires-python = ">=3.14"` in `pyproject.toml`).

Use `python3.14` (default build) or `python3.14t` (free-threaded / nogil) where available; both satisfy the version gate. The smoke CI workflow installs CPython 3.14 via `actions/setup-python`.

Threaded free-threading A/B (full config): `./bench/run_freethreading.sh` (requires `python3.14` + `python3.14t` with matching `_native` builds).


## Python API

```bash
pip install -e .
```

- `Ring(name, create=False, slot_count=64, slot_size=256, ...)`
- `try_publish(bytes)`, `try_consume()`, `wait_readable(ms)`, `Ring.unlink(name)`

Layout matches C++ — cross-language producer/consumer works.

## Examples

| Name | Language | What it demonstrates | Command |
|------|----------|----------------------|---------|
| `roundtrip` | C++ | Single-process create → publish → consume | `./build/native/roundtrip` |
| `producer` | C++ | Multi-process producer with backpressure retry | `./build/native/producer [name] [count] [delay_ms]` |
| `consumer` | C++ | Multi-process consumer with futex wait | `./build/native/consumer [name] [timeout_ms]` |
| `stress` | C++ | Fill ring until full; verify `try_publish` backpressure | `./build/native/stress` |
| `roundtrip.py` | Python | Same as C++ roundtrip | `python3 examples/python/roundtrip.py` |
| `producer.py` | Python | Same as C++ producer | `python3 examples/python/producer.py [name] [count] [delay_ms]` |
| `consumer.py` | Python | Same as C++ consumer | `python3 examples/python/consumer.py [name] [timeout_ms]` |
| `stress.py` | Python | Same as C++ stress / backpressure | `python3 examples/python/stress.py` |

**C++ producer / consumer (two terminals):** producer must create the ring first.

```bash
# terminal 1 — start producer (creates shm)
./build/native/producer smh_q_demo 10 200

# terminal 2 — consumer attaches
./build/native/consumer smh_q_demo 30000
```

**Cross-language (C++ producer, Python consumer):**

```bash
./build/native/producer smh_q_xlang 5 100 &
python3 examples/python/consumer.py smh_q_xlang 10000
```

See also [examples/cpp/README.md](examples/cpp/README.md).

## Backends

Production default is **pybind11** (`PICOIPC_BACKEND=pybind11`). ctypes and pure Python remain as fallbacks when the native extension is unavailable.

| Backend | `PICOIPC_BACKEND` | Notes |
|---------|-----------------|-------|
| pybind11 (default) | `pybind11` | Fast path; requires C++ build |
| ctypes | `ctypes` | Loads `libsmh_q.so` via ctypes |
| pure Python | `pure` | No native code; reference implementation |
| cython | `cython` | Stub only (no extension in tree); fails or falls back |

Switch backend for a single command:

```bash
export PICOIPC_BACKEND=ctypes   # or pure, pybind11
python3 -c "from picoipc import Ring, impl_name; print(impl_name())"
```

Compare all backends (smoke harness, msgs/s and speedup vs pure):

```bash
./bench/run_all_backends.sh
```

## Benchmarks

Plain `std::chrono` / `time.perf_counter` benchmarks — no external dependencies. Build C++ with Release.

| Name | Language | What it measures | Command |
|------|----------|------------------|---------|
| `bench_throughput` | C++ | Threaded SPSC: msgs/s, MB/s, p50/p99 latency | `./build/native/bench_throughput [count] [payload_bytes]` |
| `bench_sequential` | C++ | Single-thread publish-all then consume-all | `./build/native/bench_sequential [count] [payload_bytes]` |
| `bench_futex` | C++ | Spin vs futex wakeup when producer is idle | `./build/native/bench_futex [count] [idle_us]` |
| `bench_throughput.py` | Python | Threaded + sequential (same scenarios) | `python3 benchmarks/python/bench_throughput.py [count] [payload_bytes]` |

Default: 100k messages. Pass `payload_bytes=0` (Python) or omit (C++ defaults to 64) to sweep 64/256/1024 in Python.

**Sample output:**

```
$ ./build/native/bench_throughput 100000 64
threaded     payload=  64B count= 100000 elapsed=   29.80 ms  msgs/s=   3355723  MB/s=  204.82  p50=   236 ns  p99=   798 ns

$ ./build/native/bench_sequential 100000 64
sequential   payload=  64B count= 100000 elapsed=   16.94 ms  msgs/s=   5902048  MB/s=  360.23
```

## Quick start

```bash
cmake -S native -B build/native -DCMAKE_BUILD_TYPE=Release && cmake --build build/native
./build/native/roundtrip
python3 examples/python/roundtrip.py
ctest --test-dir build/native
```

## Relation to upstream SPSC ring

The upstream `ull::SpscRing` pattern backs low-latency IPC (order events, MD notify rings, etc.). This package uses the same header/cache-line/futex design; tune spin/futex via `SMH_Q_SHM_SPIN_ITERS` (default 2000) and `SMH_Q_SHM_WAIT_MS` (default 1), with the engine-specific `SMH_Q` env prefix. For local C++ bench tuning, `SMH_Q_NATIVE_ARCH=1` enables `-march=native` on the static lib and benchmarks (off by default; pybind unchanged).

## License

MIT — see [LICENSE](LICENSE).
