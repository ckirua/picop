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
