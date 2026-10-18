# picoipc — Low-Latency Local IPC

Linux-focused IPC primitives for Python and C++. The current implementation is a **single-producer / single-consumer (SPSC)** ring buffer over POSIX shared memory (`shm_open` + `mmap`) with **futex** wakeups.

The ring is a standalone `smh_q` C++ engine with no external gateway, database, or exchange runtime dependencies.

**Linux only.** Requires `shm_open`, `mmap`, and `futex`; cross-backend wire compatibility requires little-endian Linux. The pure Python backend currently supports x86_64 and requires `libatomic.so.1` (`libatomic1` on Debian/Ubuntu), including aligned lock-free 32-bit atomics. Missing atomics raise `OSError`; there is no unsynchronized fallback.

## What is SPSC and why SHM + futex?

| Concept | Meaning |
|---------|---------|
| **SPSC** | One writer, one reader. The engine publishes with acquire/release sequence counters; Python bindings also protect handle lifetime against close. |
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

**Python 3.15 is primary; Python 3.14 remains supported.** Both regular and free-threaded CPython builds are supported: 3.14, 3.15, 3.14t and 3.15t. Free-threaded imports keep the GIL disabled without an override. This does not change SPSC into MPSC.

Build each interpreter ABI separately. Source installs require a C++20 compiler, CMake, and `pybind11>=3.1.0`; build isolation installs the matching headers. For a direct native/Python build:

```bash
PYTHON="$(command -v python3.15)"
"$PYTHON" -m pip install 'pybind11>=3.1.0'
cmake -S native -B build/python315 -DSMH_Q_BUILD_PYTHON=ON \
  -DPython_EXECUTABLE="$PYTHON" \
  -Dpybind11_DIR="$("$PYTHON" -m pybind11 --cmakedir)"
cmake --build build/python315
ctest --test-dir build/python315 --output-on-failure
```

The performance gate remains the committed **3.14 pybind11** lane: `PYTHON=/path/to/python3.14 ./bench/run_gate.sh`. Correctness on the other runtimes is independent of that baseline. Threaded A/B measurements use `./bench/run_freethreading.sh` with separately built interpreter ABIs.


## Python API

```bash
pip install -e .
```

- `Ring(name, create=False, slot_count=64, slot_size=256, ...)`
- `try_publish(bytes)`, `try_consume()`, `wait_readable(ms)`, `Ring.unlink(name)`

Layout matches C++ — cross-language producer/consumer works.

`close()` is idempotent and waits for active native operations before detaching the handle. Closed publish/claim-bool/wait operations return `False`, consume/claim return `None`, sequence queries return zero, and wake does nothing. The native `publish(buf, length)` overload raises `RuntimeError("Ring is closed")`.

Native claim views and derived views retain the mapping after logical close or deletion of the Ring. Write a claimed slot only before publishing it; mapping lifetime does not make a published/reused slot safe to mutate. Native buffer operations require contiguous one-dimensional byte-sized storage, and consume destinations must be writable.

Buffer exports pin storage, not contents. Synchronize mutable source buffers and
consume destinations externally until the native operation returns.

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
| pure Python | `pure` | Reference implementation using libc/libatomic through ctypes |
| cython | `cython` | Compatibility selector re-exporting pure Python, not a separate native backend |

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
