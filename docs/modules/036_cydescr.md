# cydescr

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.descrobject` |
| Sources | `src/picop/cydescr.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

Data-descriptor checks and safe metadata introspection serve Cython type tooling. `PyDescr_New*` constructors are cimport-only: each stores its `PyMethodDef`, `PyMemberDef`, or `PyGetSetDef` pointer raw, so a Python-facing wrapper with temporary stack structures could leave dangling pointers. `PyMember_GetOne`/`PyMember_SetOne` remain low-level cimport operations; `Py_RELATIVE_OFFSET` can raise `SystemError`. `PyWrapper_New` is not exposed because its unchecked assertions require a wrapper descriptor and a compatible subclass instance. `PyDescr_NAME` and `PyDescr_TYPE` are borrowed field reads converted to owned Python references after checking descriptor type. `PyDictProxy_New` is already covered by `cydict`; no duplicate is added. `structmember.h` is deprecated; use descrobject.h definitions (`Py_T_*`, `Py_READONLY`, `Py_AUDIT_READ`, `Py_RELATIVE_OFFSET`).

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| descr_is_data | cpython.descrobject | cpdef | public | `PyDescr_IsData` |
| descr_name | cpython.descrobject | cpdef | public | checked descriptor field read |
| descr_objclass | cpython.descrobject | cpdef | public | checked descriptor owner type |
| PyDescr_NewMethod / PyDescr_NewClassMethod / PyDescr_NewMember / PyDescr_NewGetSet | C API | cdef | cimport | caller must provide static-lived struct storage |
| PyMember_GetOne / PyMember_SetOne | C API | cdef | cimport | no-steal; relative offsets can raise SystemError |
| PyDescr_NAME / PyDescr_TYPE | C API | macro | cimport | borrowed fields |
| PyWrapper_New | C API | candidate | — | not exported; unchecked asserts |
| PyDictProxy_New | cpython.dict | — | — | already covered by cydict |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| descr_is_data | APPROVED | native descriptor flag query |
| descr_name | APPROVED | checked metadata access; returns owned reference |
| descr_objclass | APPROVED | checked metadata access; returns defining type |
| PyDescr_New* | APPROVED (cimport) | static table lifetime required; unsafe as public constructor |
| PyMember_GetOne / PyMember_SetOne | APPROVED (cimport) | low-level memory API; caller controls safety and offset constraints |
| PyWrapper_New | REJECTED | unchecked assertions make safe generic public use unsuitable |
| PyDictProxy_New | APPROVED (cimport) | already implemented in cydict |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 2 |
| Last pass | 2026-11-10 — Order 069 descriptor metadata, Tier A/B |
| Next action | — |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| descr_is_data | native flag query beats Python protocol inspection | `bench/cydescr_bench.py` | 0.40x property | APPROVED | 2 |
| descr_name | native descriptor field read beats Python `__name__` | `bench/cydescr_bench.py` | 0.65x method descriptor | APPROVED | 2 |
| descr_objclass | native owner field read beats Python type lookup | `bench/cydescr_bench.py` | 0.51x method descriptor | APPROVED | 2 |
| PyDescr_New* | C-only construction useful with static tables | — | raw struct pointers require static lifetime | APPROVED (cimport) | 2 |
| PyMember_GetOne / PyMember_SetOne | C-only field access useful to extension authors | — | raw address and relative-offset errors require caller control | APPROVED (cimport) | 2 |
| PyWrapper_New | wrapper creation can be checked before CPython assertions | — | no safe wrapper exported | REJECTED | 2 |

## Bench notes

- Harness: [`bench/cydescr_bench.py`](../../bench/cydescr_bench.py)
- Tier B: [`bench/tier_b/cydescr.py`](../../bench/tier_b/cydescr.py)
- CPython 3.14.7, Linux x86_64, GIL enabled; Tier A N=80,000 × 5, Tier B N=2,000,000 × 5.

## Bench results

Harness: [`bench/cydescr_bench.py`](../../bench/cydescr_bench.py) · CPython 3.14.7 · N=80,000 × 5.

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| descr_is_data | property | 2.53±0.02ms | 2.55ms | **0.40x** | 0.39x | APPROVED |
| descr_name | method descriptor | 2.29±0.04ms | 2.35ms | **0.65x** | 0.64x | APPROVED |
| descr_objclass | method descriptor | 2.44±0.17ms | 2.72ms | **0.51x** | 0.31x | APPROVED |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cydescr.py`](../../bench/tier_b/cydescr.py) · `cydescr_tb.pyx` · CPython 3.14.7 · Linux x86_64 · N=2,000,000 × 5.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| descr_is_data | property | 6.29±0.09ms | 6.42ms | 28.77±1.26ms | **0.22x** | 0.21x | cypy faster |
| descr_name | method descriptor | 4.84±0.06ms | 4.91ms | 25.34±0.38ms | **0.19x** | 0.19x | cypy faster |
| descr_objclass | method descriptor | 4.91±0.04ms | 4.96ms | 25.81±0.22ms | **0.19x** | 0.19x | cypy faster |

## Experiment conclusions

Tier A ratios were 0.40x for `descr_is_data`, 0.65x for `descr_name`, and 0.51x for `descr_objclass`; Tier B measured `descr_is_data` at 0.22x, `descr_name` at 0.19x, and `descr_objclass` at 0.19x against typed baselines. The metadata operations use descriptor-native fields rather than Python attribute dispatch. `_is_descr` verifies supported CPython descriptor types before field access, avoiding invalid casts for arbitrary Python objects. `PyDescr_NAME` and `PyDescr_TYPE` are borrowed fields; returning their values requires a new owned reference. Constructor APIs remain cimport-only because CPython stores definition pointers without copying: static table ownership/lifetime is an ABI and safety requirement, not a convenience. `PyMember_SetOne` does not steal its input; relative-offset member definitions can fail with `SystemError`. `PyWrapper_New` remains rejected because unchecked assertions can abort on incompatible descriptor/self pairs. `PyDictProxy_New` is covered by cydict; deprecated structmember APIs are not duplicated.

## Done when

- [x] Full descriptor surface and safety decisions recorded
- [x] Public one-line stubs, tests, Tier A/B benches and usage example updated
- [x] Tier A and Tier B measurements recorded
- [ ] Integration gates passed
