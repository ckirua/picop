# cycall

| Field | Value |
|---|---|
| Status | present |
| Maps to | `Python.h` call / vectorcall APIs |
| Sources | `src/picop/cycall.{pxd,pyx,pyi}` |
| Surface | public + cimport |
| Tracker lifecycle | implementing |
| Format | v2 |
| Indexed | declared slice |

## Why

Provide GIL-held Cython call helpers that avoid temporary argument tuples for the common zero-, one-, and two-argument cases. Python callers should use normal invocation.

## Inventory

| Symbol | Kind | Export | Notes |
|---|---|---|---|
| `call_noargs` | cpdef | public + cimport | `PyObject_CallNoArgs`; new reference or raises |
| `call_onearg` | cpdef | public + cimport | `PyObject_CallOneArg`; new reference or raises |
| `call_twoargs` | cpdef | public + cimport | `PyObject_Vectorcall` with two stack arguments |
| `call_vector` | cdef | cimport | caller-owned `PyObject*` vector and keyword-name tuple |

## Safety

All helpers require the GIL. `call_vector` borrows its argument vector and keyword-name pointer for the duration of the call; callers retain ownership.

## Bench results

CPython 3.14.3, Linux x86_64, one million calls; ratio is helper / direct Python call.

| operation | helper s | direct s | ratio | verdict |
|---|---:|---:|---:|---|
| `call_noargs` | 0.0298 | 0.0144 | 2.07x | runtime convenience only |
| `call_onearg` | 0.0323 | 0.0179 | 1.81x | runtime convenience only |
| `call_twoargs` | 0.0383 | 0.0204 | 1.88x | runtime convenience only |

## Experiment conclusions

The public helpers are deliberately not Core or `picop.hot` candidates: ordinary
Python calls are faster because crossing a `cpdef` wrapper dominates. Their value
is a stable, explicit Cython call contract and a depth path that avoids building
argument tuples in extension code. The depth API is `call_vector`, which accepts
a caller-owned `PyObject*` array and keyword-name tuple; it must be exercised
only while the GIL is held and while every borrowed argument remains live.

Depth testing covered zero-, one-, and two-argument calls plus exception
propagation. A future Cython-only benchmark may promote or demote individual
helpers, but the current depth contract is intentionally cimport-oriented.
