# cyhash

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython/pyhash.h` |
| Sources | `src/picop/cyhash.*` |
| Surface | public + cimport |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

`bytearray` and `array.array` are unhashable, so the only pure-Python way to hash them is
`hash(bytes(data))` — a full copy of the buffer before the hash. `Py_HashBuffer` hashes the
bytes CPython can already read, with the interpreter's own SipHash key, so `hash_buffer`
removes the copy, the allocation, and the buffer-protocol round trip. The raw-pointer helpers
(`hash_buffer_raw`, `hash_pointer`, `hash_generic`) stay cimport-only: they take unverified
pointers or skip a type's own `__hash__`, which is a trusted-caller decision, not a Python API.

## Inventory

Full public surface of `cpython/pyhash.h` in CPython 3.14/3.15, plus the internals the header
references.

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| `Py_HashBuffer` | C-API | function | `hash_buffer` | Public; `start`/`end` give a range without a slice copy; added 3.14 |
| `Py_HashPointer` | C-API | function | `hash_pointer` | cimport-only; added 3.13, cannot return `-1` |
| `PyObject_GenericHash` | C-API | function | `hash_generic` | cimport-only identity hash; CPython == `Py_HashPointer` |
| `PyHash_GetFuncDef` | C-API | function | — | Hash-algorithm introspection; not a hot path |
| `_Py_HashPointer` | deprecated alias | inline | — | `Py_DEPRECATED(3.14)`; use `Py_HashPointer` |
| `_Py_HashPointerRaw` | internal (`pycore_pyhash.h`) | inline | — | Internal ABI; no public wrapper |
| `Py_HASH_CUTOFF` / `Py_HASH_*` | C-API | macro | — | Build-time algorithm configuration, not callable |
| `PyHash_Func` | C-API | global | — | Embedder hook (deprecated 3.15); out of scope |
| `hash_buffer_raw` | picop | cdef inline | cimport | Trusted-caller pointer + length, `noexcept` |
| `hash_buffer` range form | picop | cpdef | public | `end=-1` means "to the end"; out-of-range raises `ValueError` |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| `hash_buffer` | APPROVED | Tier A 0.40–0.78x on exporters Python cannot hash; Tier B 0.23–0.37x |
| `hash_buffer` range form | APPROVED | Tier A 0.54–0.58x; the builtin route must build a slice object first |
| `hash_buffer` on cached objects | APPROVED, documented loss | `bytes`/`memoryview` cache their hash, so re-hashing loses (1.34–3.09x) |
| `hash_buffer_raw` | APPROVED (cimport) | Tier B 0.38–0.39x against typed copy-and-hash |
| `hash_pointer` | APPROVED (cimport) | Tier B 0.65–0.67x against builtin `hash()` on identity-hashed objects |
| `hash_generic` | APPROVED (cimport) | Tier B 0.77–0.78x; skips the `tp_hash` dispatch and the builtin lookup |
| `PyHash_GetFuncDef` | REJECTED | Returns a struct describing the hash algorithm; diagnostic, not a hot path |
| `_Py_HashPointer` / `_Py_HashPointerRaw` | REJECTED | Deprecated alias and internal header; public equivalents already wrapped |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-11-09 — full inventory, Tier A try-all + depth pass, Tier B checks, hash-cache crossover probe |
| Next action | None; no subsequent queue order is inferred |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| `hash_buffer` | Skipping `bytes(data)` beats copy-then-hash | Tier A, 7 cases | 0.40–0.78x on unhashable exporters | APPROVED | 0 |
| `hash_buffer` ranges | A `start`/`end` pair avoids the slice object | Tier A range cases | 0.54–0.58x vs `hash(data[a:b])` | APPROVED | 0 |
| `hash_buffer` on `bytes`/`memoryview` | Wrapper should beat `hash(x)` for any buffer | Tier A + probe | cached `bytes` 1.34x, cached `memoryview` 3.09x; cold `bytes` 1.02x | keep, documented crossover | 1 |
| `hash_pointer` / `hash_generic` | Direct C calls beat builtin dispatch | Tier B typed loops | 0.65–0.78x | APPROVED (cimport) — identity hashing is a Cython-only concern | 0 |
| non-contiguous buffers | `PyBUF_SIMPLE` might hash the underlying block silently | probe | `BufferError: memoryview: underlying buffer is not C-contiguous` | safe: CPython refuses the buffer before any hashing | 0 |
| `PyHash_GetFuncDef` | Algorithm introspection could help portability | API review | diagnostic struct, no measurable hot path | REJECTED | 0 |

## Bench notes

- Harness: [`bench/cyhash_bench.py`](../../bench/cyhash_bench.py)
- Tier B harness: [`bench/tier_b/cyhash.py`](../../bench/tier_b/cyhash.py) (`bench/tier_b/cyhash_tb.pyx`)
- Gate: [`docs/README.md`](../README.md) (mean ratio ≤ 0.95) — `hash_buffer` passes on every
  case where the plain-Python route is a copy; the cached-object cases are recorded as a
  documented loss in `docs/PERF_PARITY.md` rather than hidden from the mean.
- Environment: CPython 3.15.0rc2, Linux x86_64, GIL build; Tier A default N=80,000 × RUNS=5,
  depth N=500,000 × RUNS=11; Tier B N=2,000,000 and N=8,000,000, 5 runs each.

## Bench results

### Tier A (public helper vs plain Python)

Default pass, `CPY_BENCH_N=80,000`, `CPY_BENCH_RUNS=5` — mean **1.04x**, 5/7 cases faster:

|case|picop ns/op|Python ns/op|Mean ratio|Runs|
|---|---:|---:|---:|---:|
|`bytearray` n=64|79.4|176.4|0.44x|5|
|`bytearray` n=2048|548.5|709.6|0.77x|5|
|`array.array('B')` n=6|67.1|168.3|0.40x|5|
|`bytes` n=2048 range 64:128|79.4|136.6|0.58x|5|
|`memoryview` n=256 range 64:128|83.0|154.8|0.54x|5|
|`bytes` n=8 (cached)|64.8|48.3|1.34x|5|
|`memoryview` n=256 (cached)|124.6|40.3|3.09x|5|

The first five cases are the ones `hash_buffer` exists for: `bytearray`, `array.array`, and a
range that the builtin has to materialise as a slice object. The last two are the crossover,
measured deliberately.

Depth pass, `CPY_BENCH_N=500,000`, `CPY_BENCH_RUNS=11` — mean **1.06x**:

|case|ratio|
|---|---:|
|`bytearray` n=64|0.44x|
|`bytearray` n=2048|0.77x|
|`array.array('B')` n=6|0.41x|
|`bytes` n=2048 range 64:128|0.59x|
|`memoryview` n=256 range 64:128|0.53x|
|`bytes` n=8 (cached)|1.52x|
|`memoryview` n=256 (cached)|3.07x|

### Tier B (typed Cython loop)

`CPY_TIERB_N=2,000,000`, 5 runs:

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| `hash_buffer(memoryview)` | vs copy + hash | 82.33±13.49ms | 97.77ms | 232.58±2.17ms | **0.35x** | 0.42x | cypy faster |
| `hash_buffer(range 8:56)` | vs slice copy + hash | 65.40±0.93ms | 66.80ms | 288.96±0.85ms | **0.23x** | 0.23x | cypy faster |
| `hash_buffer(memoryview)` | vs cached `hash(mv)` | 71.89±0.86ms | 73.15ms | 6.70±0.43ms | **10.74x** | 9.89x | baseline faster |
| `hash_generic` | vs builtin `hash()` | 5.50±0.36ms | 6.10ms | 7.03±0.12ms | **0.78x** | 0.85x | cypy faster |
| `hash_pointer` | vs builtin `hash()` | 4.60±0.04ms | 4.66ms | 7.13±0.42ms | **0.65x** | 0.59x | cypy faster |
| `hash_buffer_raw` (raw pointer) | vs copy + hash | 46.00±1.36ms | 48.06ms | 120.16±1.27ms | **0.38x** | 0.39x | cypy faster |

Depth pass, `CPY_TIERB_N=8,000,000`, 5 runs: 0.37x, 0.25x, 11.07x, 0.77x, 0.67x, 0.39x — same
ordering.

## Experiment conclusions

- **The win is the copy, not the hash.** For `bytearray` and `array.array` there is no
  pure-Python hash at all, so the baseline is `hash(bytes(data))`. At n=64 the wrapper costs
  0.44x of that (79.4 ns against 176.4 ns); at n=2048 it is 0.77x, because the SipHash itself
  is the same O(n) work in both paths and only the memcpy disappears. `hash_buffer` is a win
  exactly where CPython cannot hash the object.
- **Cached objects are the crossover, and it is a cache, not the algorithm.** `bytes` and
  `memoryview` store their hash on the object after the first call, so `hash(mv256)` is 40.3 ns
  regardless of length while `hash_buffer` re-hashes 256 bytes every time (124.6 ns, 3.09x). A
  probe over 1024 *cold* `bytes` objects (never hashed) gives 583.6 ns for `hash()` against
  595.5 ns for `hash_buffer` — 1.02x, i.e. the two paths are identical when the cache is empty.
  Tier B makes the same point with a typed loop: 71.9 ms for `hash_buffer` against 6.7 ms for
  the cached builtin (10.74x).
- **Ranges win because a slice is an object.** `mv[64:128]` allocates a new `memoryview`
  (154.8 ns total for the builtin path) before hashing; `hash_buffer(mv, 64, 128)` is 83.0 ns.
  The same holds for `bytes`, where `b[64:128]` copies 64 bytes: 0.58x.
- **Non-contiguous buffers are refused, not mis-hashed.** `PyObject_GetBuffer(...,
  PyBUF_SIMPLE)` on `memoryview(data)[::2]` raises `BufferError: memoryview: underlying buffer
  is not C-contiguous` before any hashing, so a strided view can never produce a hash of the
  wrong bytes. Offset views (`mv[3:]`) are contiguous and hash correctly.
- **Sentinel and ownership.** `Py_HashBuffer` and `Py_HashPointer` both map a raw `-1` result
  to `-2` before returning (`Python/pyhash.c`), so neither helper can ever return the `-1`
  sentinel and `hash_buffer` matches `hash(bytes(...))` bit for bit — including the empty
  buffer, which is defined to hash to `0`. No reference is taken or stolen: the helper returns
  a C integer, and the `Py_buffer` is released in a `finally` block on every path, including
  the `ValueError` range check, so a bad range cannot leak the buffer.
- **Free-threading.** `Py_HashBuffer` reads the process-wide hash secret and writes nothing; the
  module is marked `freethreading_compatible` and the stress suite confirms identical results
  across 12 threads on the 3.15 free-threaded build.
- **Demotion rationale.** `hash_pointer` and `hash_generic` are identity hashes that silently
  ignore a type's own `__hash__` — a correctness trap if exposed to Python callers, and only a
  win inside typed Cython code (0.65–0.78x), so both stay cimport-only.
- **Rejected internals.** `_Py_HashPointerRaw` lives in `internal/pycore_pyhash.h`; wrapping it
  would depend on non-public ABI (see [`docs/SAFETY.md`](../SAFETY.md)).

## Done when

- [x] Full inventory vs mapped include (`pyhash.h` public symbols covered or rejected)
- [x] Every row has workflow status
- [x] Lifecycle + next action filled
- [x] APPROVED / APPROVED (cimport) rows have decision-log evidence
- [x] REJECTED rows have policy or measured why
- [x] Present measuring: try-all and depth checklist recorded in this tracker
- [x] Bench results table filled in this file
- [x] Public PEP 257 docstring in `cyhash.pyi`; `.pxd` lean
