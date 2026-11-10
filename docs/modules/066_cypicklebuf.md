# cypicklebuf

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython/picklebufobject.h` (CPython 3.15+) |
| Sources | `src/picop/cypicklebuf.*`, `src/picop/cypicklebuf_shim.h` |
| Surface | public + cimport |
| Tracker lifecycle | decided (Tier A + Tier B + depth) |
| Format | v2 |
| Indexed | full |

## Why

Expose CPython's buffer-backed pickle transport object for serializers and Cython code that needs the exact `PickleBuffer` API. Creation, release, exact-type check, and type object have safe Python-facing forms. `PyPickleBuffer_GetBuffer` returns a pointer into the PickleBuffer's owned export; it is cimport-only because a raw pointer can outlive its owner. Releasing the PickleBuffer invalidates that storage, so no borrowed memoryview wrapper is returned. CPython 3.14 lacks the C API; the module compiles there but its operations raise `NotImplementedError` instead of pretending to implement the 3.15 API.

## Inventory

Full callable/public surface of `cpython/picklebufobject.h` in CPython 3.15. `PyPickleBuffer_Check` is a macro and performs exact type identity via `Py_IS_TYPE`; there is no CheckExact alias. `PyPickleBuffer_GetObj` is absent.

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| `PyPickleBuffer_FromObject` | C-API | function | `pickle_buffer_from_object` | Owns a buffer export; raises TypeError for non-buffer objects |
| `PyPickleBuffer_Release` | C-API | function | `pickle_buffer_release` | Invalidates buffer access; only exact PickleBuffer instances accepted |
| `PyPickleBuffer_Check` | C-API | macro | `pickle_buffer_check` | Exact-type check, not subclass check |
| `PyPickleBuffer_GetBuffer` | C-API | function | `pickle_buffer_get_buffer` | cimport-only raw pointer; valid only while its PickleBuffer remains alive and unreleased |
| `PyPickleBuffer_Type` | C-API | global | `pickle_buffer_type` | Python type object |
| `PyPickleBuffer_CheckExact` | C-API | candidate | — | REJECTED: absent from 3.15 public header; Check already exact |
| `PyPickleBuffer_GetObj` | C-API | candidate | — | REJECTED: absent from 3.15 public header |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| `pickle_buffer_from_object` | APPROVED | Implements PickleBuffer semantics required for protocol-5 out-of-band buffer flow; Tier A is slower than `memoryview` construction (1.62–2.16x) but 0.10x the cost of serializing a buffer-backed record; loss and semantic distinction documented in stub and parity table |
| `pickle_buffer_release` | APPROVED | Core release operation; tests verify the object refuses a new memoryview after release |
| `pickle_buffer_check` | APPROVED | Direct wrapper of header macro's exact-type behavior |
| `pickle_buffer_type` | APPROVED | Direct accessor for exported public type object |
| `pickle_buffer_get_buffer` | APPROVED (cimport) | Pointer borrowed from object; unsafe to return as Python object because release invalidates it |
| `PyPickleBuffer_CheckExact` | REJECTED | Header inspection: no such declaration; `PyPickleBuffer_Check` uses exact type identity |
| `PyPickleBuffer_GetObj` | REJECTED | Header inspection: no such declaration in CPython 3.15 `cpython/picklebufobject.h` |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-11-10 — full header inventory, Tier A/Tier B measurement, release and shape probes |
| Next action | None |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| `pickle_buffer_from_object` | C API construction provides a buffer-backed pickle object directly | `bench/cypicklebuf_bench.py` | 1.62–2.16x vs memoryview construction; 0.10x vs serializing a buffer-backed record | APPROVED as protocol semantic API; slower plain-Python path documented | 1 |
| `pickle_buffer_from_object` | Cost changes with exporter size | Tier A 6/248/4096 bytes | 2.16x / 1.70x / 1.62x vs memoryview | Wrapping cost dominates small inputs; lower relative cost for 4 KiB, still slower | 1 |
| `pickle_buffer_get_buffer` | Exposing buffer to Python risks pointer lifetime misuse | Cython cimport smoke | Non-NULL while live; NULL after release | APPROVED (cimport) | 1 |
| `PyPickleBuffer_Release` | Release invalidates buffer access | test + Cython smoke | new memoryview acquisition fails; direct GetBuffer pointer becomes NULL | APPROVED | 1 |
| absent exact/get-object APIs | Candidate APIs may be exposed | CPython 3.15 header scan | absent | REJECTED | 1 |

## Bench notes

- Harness: [`bench/cypicklebuf_bench.py`](../../bench/cypicklebuf_bench.py)
- Tier B harness: [`bench/tier_b/cypicklebuf.py`](../../bench/tier_b/cypicklebuf.py) (`bench/tier_b/cypicklebuf_tb.pyx`)
- Gate: [`docs/README.md`](../README.md) (mean ratio ≤ 0.95); plain memoryview construction is faster because it does not allocate PickleBuffer's pickle-protocol wrapper. Direct pickle serialization is much slower.
- Environment: CPython 3.15.0rc2, Linux x86_64, GIL build; Tier A N=10,000, RUNS=5; Tier B N=2,000,000 × 5 runs.

## Bench results

### Tier A

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| `pickle_buffer_from_object` | bytearray n=6 vs memoryview | 2.08±1.47 ms | 4.55 ms | 2.16x | 4.52x | baseline faster |
| `pickle_buffer_from_object` | bytearray n=248 vs memoryview | 1.68±0.35 ms | 2.06 ms | 1.70x | 1.80x | baseline faster |
| `pickle_buffer_from_object` | bytearray n=4096 vs memoryview | 1.56±0.33 ms | 1.94 ms | 1.62x | 2.00x | baseline faster |
| `pickle_buffer_from_object` | buffer-backed record creation vs `pickle.dumps` | 1.89±0.38 ms | 2.36 ms | 0.10x | 0.07x | picop faster; not a semantic replacement for memoryview |

### Tier B

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | verdict |
|-----------|------|-------------|-----|----------------|-------|------|---------|
| `pickle_buffer_from_object` | bytearray vs typed memoryview creation, N=2,000,000 | 288.16±71.66 ms | 409.44 ms | 129.07±12.56 ms | 2.23x | 2.82x | baseline faster |

## Experiment conclusions

Why the helper loses to `memoryview`: PickleBuffer construction adds protocol-specific wrapper allocation and ownership state that a plain view does not provide. Scale measurements across 6, 248, and 4096 bytes show the gap declining from 2.16x on 6 B to 1.70x at 248 B and 1.62x at 4 KiB, but still slower than `memoryview(obj)`. Against complete `pickle.dumps` of a custom buffer-backed record, direct PickleBuffer creation is 0.10x the measured cost because it constructs the protocol object without serializing the record. Tier B's typed loop repeats the same operation 2,000,000 times and shows 2.23x vs memoryview construction; the C API wrapper's allocation/ownership work dominates. Keep the Python API for protocol semantics, not as a faster general view constructor, and document this mixed Tier A parity in `.pyi` and `PERF_PARITY.md`.

`PyPickleBuffer_GetBuffer` returns NULL after release and CPython sets `ValueError` on that call; the cimport smoke observes a valid non-NULL pointer while live and the post-release error corresponding to the NULL result. A previously acquired Python memoryview holds its own export and remains valid until that view is released; acquiring a new view from the released PickleBuffer also raises `ValueError`. Therefore the direct pointer stays cimport-only and callers must keep the owning PickleBuffer alive and unreleased throughout pointer use. CPython 3.14 build compiles through the version shim and calls fail explicitly with `NotImplementedError`; usable implementations require 3.15+. Header ABI inspection confirmed the API is present on 3.15, and no `GetObj` or `CheckExact` exists.

## Done when

- [x] Full header inventory and candidate APIs recorded
- [x] Candidate decisions grounded in header evidence
- [x] Tier A/Tier B and depth probes written under Experiment conclusions
- [x] Bench results table filled in this file
- [x] Public PEP 257 summaries and version/performance caveat in `.pyi`; `.pxd` lean
