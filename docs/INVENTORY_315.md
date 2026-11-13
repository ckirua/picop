# CPython 3.15 header inventory (2026-11-12)

Method: set-diff of `PyAPI_FUNC`/`PyAPI_DATA`/opaque typedefs between CPython **3.14.7** and **3.15.0rc2** headers (238 new, 37 removed), cross-checked against every `src/picop/*.pxd|pyx|py|h|pyi` reference, then verified exported in the 3.15 binary via `nm`. Linkable candidates below are queue-ready; internals are indexed with a mechanism note, per the PIPELINE "no silent skip" rule.

## New public API — promotable

| API | Symbol(s) | Verdict | Next action |
|-----|-----------|---------|-------------|
| BytesWriter public writer API (new in 3.15, PEP 782) | `PyBytesWriter_Create`, `WriteBytes`, `Resize`, `Finish`, `Discard` | **Order 075** (extends 002) — shipped | `BytesWriter(max_size)` honours the hint on 3.15+ via `Create(hint)` + `Resize(0)` (Resize sets the logical size, so rewinding to 0 keeps the allocation as reserved capacity) |
| Public tuple builder | `PyTuple_FromArray` | **Order 076** (extends 001) — shipped | `tuple_from_array` cimport helper; loop fallback pre-3.15 |
| Interpreter view / guard (free-threading-safe thread state) | `PyInterpreterView_FromCurrent/FromMain/Close`, `PyInterpreterGuard_FromCurrent/FromView/Close`, `PyThreadState_Ensure/EnsureFromView/Release` | **Order 077** (extends 012) — shipped | `interpreter_guard()` CM + `guards_supported()` public; raw helpers cimport-only, GILState fallback pre-3.15 |
| Immortal set | `PyUnstable_SetImmortal` | **Order 078** (extends 028) — shipped | `ref_set_immortal` cimport helper; 3.14 refcount-pin emulation |
| Lazy-import mode | `PyImport_Get/SetLazyImportsMode/Filter`, `PyLazyImport_Type` | **Order 079** (extends 068) — shipped | public mode probe/get/set; filters cimport-only; `PyLazyImport_Type` rejected (internal header) |

## New public API — indexed, no demand

| API | Why not wrapped |
|-----|-----------------|
| `PyArg_ParseArray(AndKeywords)` | Argument-parsing convenience; picop's niche is hot accessors, not arg-parsing |
| `PyModule_Exec`, `PyModule_FromSlotsAndSpec`, `PyModule_GetStateSize`, `PyType_FromSlots`, `PyABIInfo`, `PyModule_GetToken` | Extension-authoring scaffolding; high churn, low call-site demand |
| `*_DuringGC` accessors (`PyModule_GetState_DuringGC`, `PyType_GetModule_DuringGC`, …) | Valid only inside GC traversal context; niche for picop consumers |
| `PyObject_Dump`, `PyUnstable_DumpTraceback*` | Debug aids; no benchmarkable win |
| `PyExc_ImportCycleError` | picop wraps no exception-type constants; available natively via `picop` consumers |
| `Py_IS_TYPE`, `Py_SIZE`, `Py_SET_SIZE` | Now public macros — already used internally by picop, no wrapper needed |

## New internals — REJECTED (volatility)

`_PyJit*`/`_PyUOpInstruction`/`_Py_Specialize_*` (JIT executor internals, change per release), `_PyDictKeys_*`/`_PyDict_InsertSplitValue`/`_PyDict_*_LockHeld` (dict keys-split internals, no ABI contract), `_PyFrame_*`/`_PyStackRef*`/`_PyThreadState_PushFrame` (frame/stackref rewrite, version-coupled), `_PyCompactLong_*` (renamed from `_PyLong_*`, private), `_PyCode_GetTLBC`/`_PyCode_InitAddressRange` (code address-range tables), `_PySlotIterator_*`, `_PyUOpsAbstractFrame`. All fail the "non-static, stable enough to link" test for public wrappers; Tier B call sites keep using the object APIs.

## Removed in 3.15 — picop exposure

| Removed | picop status |
|---------|--------------|
| `_PyBytesWriter_Init/Alloc/Prepare/Resize/Finish/Dealloc/WriteBytes` | Already guarded: shim mirrors these only under `#if PY_VERSION_HEX < 0x030F0000` (Order 074); 3.15 uses the public API. CI green |
| `PyWeakref_GetObject`, legacy `PyUnicode_As*Codec*`, `Py_Get*` (program paths), `PySys_ResetWarnOptions`, `PyImport_ImportModuleNoBlock` | Never wrapped |
| `_PyLong_Add/Multiply/Subtract`, `_PyTuple_FromArray`, `_PyCode_ConstantKey`, `_PyDict_MergeEx`, `_PyTime_AsLong/FromLong` | Never wrapped |

## Queue

080 BytesWriter getters/Grow (002) — no other 3.15 gap currently blocks the queue.

## Fresh scan — 2026-11-13

Method: full re-enumeration of `PyAPI_FUNC`/`PyAPI_DATA` declarations in **every** public header of the installed 3.15.0rc2 tree (`include/python3.15/` + `include/python3.15/cpython/`, 139 public headers of 287 total; 148 `internal/` headers excluded by policy), word-boundary checked against every `src/picop/*.pxd|pyx|py|h|pyi` reference, then re-diffed against the 3.14.7 headers to isolate 3.15-only names.

| item | count |
|------|-------|
| new-in-3.15 public symbols re-derived | **50** (49 `PyAPI_FUNC`, 1 `PyAPI_DATA`) |
| already linked by picop (Orders 075–079 + earlier) | **22** |
| indexed or rejected (no demand / internals) | **21** |
| new promotable candidates | **7** — all remaining `PyBytesWriter` functions |

New promotable candidates (all `cpython/bytesobject.h`, all `PyAPI_FUNC`, all confirmed exported in the 3.15 binary by `nm`):

| API | Symbol(s) | Verdict | Next action |
|-----|-----------|---------|-------------|
| BytesWriter getters / low-level growth | `GetSize`, `GetData`, `Grow`, `GrowAndUpdatePointer`, `FinishWithSize`, `FinishWithPointer`, `Format` | **Order 080** (extends 002) | `writer_size()` / `writer_data()` accessors, `grow(n)` for chunked producers, `finish_with_size(n)` for pre-computed lengths; bench `Grow`-based writes vs `bytearray` and vs `b"".join`. `Format` is varargs — wrap only if a bench case justifies it |

Corrections to the 2026-11-12 scan:

1. **`PyBytesWriter` is entirely new in 3.15 (PEP 782), not an extension of an existing writer.** `grep PyBytesWriter_` over the 3.14.7 tree returns zero hits; picop's 3.14 path mirrors the internal `_PyBytesWriter` struct.
2. **`PyBytesWriter_Resize` semantics.** It resizes the writer to `size` bytes (grow or shrink; newly allocated bytes uninitialized) — it sets the *logical* size, it is not a pure reservation. Order 075's shipped trick is `Create(hint)` + `Resize(0)`: allocate with the hint, rewind the size. `Grow(writer, n)` adds `n` to the current size (may be negative).
3. **`PyDict_SetDefaultRef`** is not new as a symbol (present in 3.14); it is merely promoted to the Limited API in 3.15. picop already links it.
4. **`PyObject_Dump`** (3.15) replaces the deprecated `_PyObject_Dump`; `_PyObject_GetAttrId` is now `Py_DEPRECATED(3.15)`; `_PyBytes_Join`/`_PyBytes_Resize` are soft-deprecated in favour of the writer API. No picop code touches any of them.

Negative checks: `PyModule_GetSlots` and `PyModule_GetWarningsModule` are declared nowhere in 3.15; `_PyStructSequence_NewType` stays internal (`internal/pycore_structseq.h`). Everything else in the 50-symbol delta is either token/GC-traversal-gated, embedding-only, debug-only, or already mirrored by existing helpers.
