# CPython 3.15 header inventory (2026-11-12)

Method: set-diff of `PyAPI_FUNC`/`PyAPI_DATA`/opaque typedefs between CPython **3.14.7** and **3.15.0rc2** headers (238 new, 37 removed), cross-checked against every `src/picop/*.pxd|pyx|py|h|pyi` reference, then verified exported in the 3.15 binary via `nm`. Linkable candidates below are queue-ready; internals are indexed with a mechanism note, per the PIPELINE "no silent skip" rule.

## New public API — promotable

| API | Symbol(s) | Verdict | Next action |
|-----|-----------|---------|-------------|
| BytesWriter 3.15 extensions | `PyBytesWriter_Grow`, `GrowAndUpdatePointer`, `Resize`, `FinishWithSize`, `FinishWithPointer`, `GetData`, `GetSize`, `Format` | **Order 075** | Honours `max_size` hint on 3.15+ via `Grow` (currently ignored there — see 002 tracker); add `finish(size)` variant |
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

075 BytesWriter Grow (002) → 076 PyTuple_FromArray (001) → 077 cythread interpreter views (012) → minor: SetImmortal (026), lazy-import mode (068).
