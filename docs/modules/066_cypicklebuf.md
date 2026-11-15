# cypicklebuf

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython/picklebufobject.h` (public C-API in every supported interpreter: 3.14 and 3.15) |
| Sources | `src/picop/cypicklebuf.*`, `src/picop/cypicklebuf_shim.h` |
| Surface | public + cimport |
| Tracker lifecycle | decided (Tier A + Tier B + depth) |
| Format | v2 |
| Indexed | full |

## Why

Expose CPython's buffer-backed pickle transport object for serializers and Cython code that needs the exact `PickleBuffer` API. Creation, release, exact-type check, and type object have safe Python-facing forms. `PyPickleBuffer_GetBuffer` returns a pointer into the PickleBuffer's owned export; it is cimport-only because a raw pointer can outlive its owner. Releasing the PickleBuffer invalidates that storage, so no borrowed memoryview wrapper is returned. The header was mis-read as 3.15-only at first, which made the shim refuse to call it on 3.14; `cpython/picklebufobject.h` declares all four functions on 3.14 as well (verified by header inspection and exported symbols in the 3.14.7 binary), so the shim now has no version branch.

## Inventory

Full callable/public surface of `cpython/picklebufobject.h` (declarations identical in 3.14.7 and 3.15.0rc2). `PyPickleBuffer_Check` is a macro and performs exact type identity via `Py_IS_TYPE`; there is no CheckExact alias. `PyPickleBuffer_GetObj` is absent.

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
| Iteration | 2 |
| Last pass | 2026-11-15 — Order 081: the shim's 3.15-only guard removed, helpers exercised on CPython 3.14.7 and 3.15.0rc2, Tier A re-measured on both |
| Next action | None |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| `pickle_buffer_from_object` | C API construction provides a buffer-backed pickle object directly | `bench/cypicklebuf_bench.py` | 1.62–2.16x vs memoryview construction; 0.10x vs serializing a buffer-backed record | APPROVED as protocol semantic API; slower plain-Python path documented | 1 |
| `pickle_buffer_from_object` | Cost changes with exporter size | Tier A 6/248/4096 bytes | 2.16x / 1.70x / 1.62x vs memoryview | Wrapping cost dominates small inputs; lower relative cost for 4 KiB, still slower | 1 |
| `pickle_buffer_get_buffer` | Exposing buffer to Python risks pointer lifetime misuse | Cython cimport smoke | Non-NULL while live; NULL after release | APPROVED (cimport) | 1 |
| `PyPickleBuffer_Release` | Release invalidates buffer access | test + Cython smoke | new memoryview acquisition fails; direct GetBuffer pointer becomes NULL | APPROVED | 1 |
| absent exact/get-object APIs | Candidate APIs may be exposed | CPython 3.15 header scan | absent | REJECTED | 1 |
| `pickle_buffer_*` on CPython 3.14 | The shim's `PY_VERSION_HEX >= 0x030F0000` guard assumed the C API is 3.15-only | header grep of `cpython/picklebufobject.h` in 3.14.7, `nm -D` on the 3.14.7 binary, `bench/cypicklebuf_bench.py` on 3.14.7, `tests/test_cypicklebuf.py` on 3.14.7 | all four symbols exported on 3.14.7; 5/5 tests pass; Tier A ratios 2.09–3.53x vs memoryview, 0.22x vs `pickle.dumps` — identical shape to 3.15 | REJECTED guard: the version branch was wrong and made the public helpers raise `NotImplementedError` on 3.14, which crashed the perf-parity bench job | 2 |

## Bench notes

- Harness: [`bench/cypicklebuf_bench.py`](../../bench/cypicklebuf_bench.py)
- Tier B harness: [`bench/tier_b/cypicklebuf.py`](../../bench/tier_b/cypicklebuf.py) (`bench/tier_b/cypicklebuf_tb.pyx`)
- Gate: [`docs/README.md`](../README.md) (mean ratio ≤ 0.95); plain memoryview construction is faster because it does not allocate PickleBuffer's pickle-protocol wrapper. Direct pickle serialization is much slower.
- Environment: CPython 3.15.0rc2, Linux x86_64, GIL build; Tier A N=10,000, RUNS=5; Tier B N=2,000,000 × 5 runs.
- Free-threading: `cypicklebuf.pyx` declares `freethreading_compatible=True`; verified on CPython 3.15.0rc2 free-threaded, where `tests/test_freethreading.py` keeps the GIL disabled after importing `picop.cypicklebuf`.

## Bench results

### Tier A (CPython 3.14.7 — helpers live here now; measured 2026-11-15)

| operation | case | picop mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| `pickle_buffer_from_object` | bytearray n=6 vs memoryview | 15.96±7.01 ms | 27.82 ms | 2.09x | 3.58x | baseline faster |
| `pickle_buffer_from_object` | bytearray n=248 vs memoryview | 27.29±21.35 ms | 56.61 ms | 3.53x | 7.28x | baseline faster |
| `pickle_buffer_from_object` | bytearray n=4096 vs memoryview | 24.40±27.58 ms | 71.29 ms | 3.18x | 9.16x | baseline faster |
| `pickle_buffer_from_object` | buffer-backed record creation vs `pickle.dumps` | 30.54±34.10 ms | 88.52 ms | 0.22x | 0.42x | picop faster; not a semantic replacement for memoryview |

### Tier A (CPython 3.15.0rc2, re-measured 2026-11-15)

| operation | case | picop mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| `pickle_buffer_from_object` | bytearray n=6 vs memoryview | 15.89±7.02 ms | 27.77 ms | 2.18x | 3.75x | baseline faster |
| `pickle_buffer_from_object` | bytearray n=248 vs memoryview | 27.14±21.46 ms | 56.78 ms | 3.72x | 7.64x | baseline faster |
| `pickle_buffer_from_object` | bytearray n=4096 vs memoryview | 24.31±27.51 ms | 71.08 ms | 3.35x | 9.69x | baseline faster |
| `pickle_buffer_from_object` | buffer-backed record creation vs `pickle.dumps` | 30.69±35.55 ms | 91.13 ms | 0.18x | 0.33x | picop faster; not a semantic replacement for memoryview |

### Tier B (iteration 1, CPython 3.15.0rc2)

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | verdict |
|-----------|------|-------------|-----|----------------|-------|------|---------|
| `pickle_buffer_from_object` | bytearray vs typed memoryview creation, N=2,000,000 | 288.16±71.66 ms | 409.44 ms | 129.07±12.56 ms | 2.23x | 2.82x | baseline faster |

## Experiment conclusions

Why the helper loses to `memoryview`: PickleBuffer construction adds protocol-specific wrapper allocation and ownership state that a plain view does not provide. Re-measured across 6, 248, and 4096 bytes on both interpreters the wrapper costs 2.09–2.18x on 6 B, 3.53–3.72x at 248 B and 3.18–3.35x at 4 KiB versus `memoryview(obj)` (iteration 1 read 1.62–2.16x on a quieter machine; the ordering — wrapper slower at every size — is unchanged). Against complete `pickle.dumps` of a custom buffer-backed record, direct PickleBuffer creation is 0.18–0.22x the measured cost because it constructs the protocol object without serializing the record. Tier B's typed loop repeats the same operation 2,000,000 times and shows 2.23x vs memoryview construction; the C API wrapper's allocation/ownership work dominates. Keep the Python API for protocol semantics, not as a faster general view constructor, and document this mixed Tier A parity in `.pyi` and `PERF_PARITY.md`.

`PyPickleBuffer_GetBuffer` returns NULL after release and CPython sets `ValueError` on that call; the cimport smoke observes a valid non-NULL pointer while live and the post-release error corresponding to the NULL result. A previously acquired Python memoryview holds its own export and remains valid until that view is released; acquiring a new view from the released PickleBuffer also raises `ValueError`. Therefore the direct pointer stays cimport-only and callers must keep the owning PickleBuffer alive and unreleased throughout pointer use. The shim's `PY_VERSION_HEX >= 0x030F0000` branch (which made every call raise `NotImplementedError` on 3.14) was a misread of the header: 3.14.7 declares all four functions in `cpython/picklebufobject.h` and exports `PyPickleBuffer_FromObject`, `PyPickleBuffer_GetBuffer`, `PyPickleBuffer_Release` and `PyPickleBuffer_Type`, so the helpers behave identically on 3.14 and 3.15 (Tier A ratios differ by under 0.2x). Header inspection shows no `GetObj` or `CheckExact` in either interpreter.

## Done when

- [x] Full header inventory and candidate APIs recorded
- [x] Candidate decisions grounded in header evidence
- [x] Tier A/Tier B and depth probes written under Experiment conclusions
- [x] Bench results table filled in this file
- [x] Public PEP 257 summaries and version/performance caveat in `.pyi`; `.pxd` lean
