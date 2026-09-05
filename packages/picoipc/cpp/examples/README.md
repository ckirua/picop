# C++ examples and benchmarks

Build from `cpp/`:

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build
```

## Examples

| Binary | Source | Description |
|--------|--------|-------------|
| `roundtrip` | `roundtrip.cpp` | Single-process publish/consume sanity check |
| `producer` | `producer.cpp` | Writes numbered messages; args: `[name] [count] [delay_ms]` |
| `consumer` | `consumer.cpp` | Reads until timeout; args: `[name] [timeout_ms]` |
| `stress` | `stress.cpp` | Fills a 4-slot ring; verifies backpressure |

## Benchmarks

| Binary | Source | Description |
|--------|--------|-------------|
| `bench_throughput` | `../benchmarks/bench_throughput.cpp` | Threaded SPSC; args: `[count] [payload_bytes]` |
| `bench_sequential` | `../benchmarks/bench_sequential.cpp` | Publish-all then consume-all; args: `[count] [payload_bytes]` |
| `bench_futex` | `../benchmarks/bench_futex.cpp` | Spin vs futex consumer; args: `[count] [idle_us]` |
