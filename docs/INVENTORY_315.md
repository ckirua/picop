# CPython 3.15 header inventory

**Method (machine-derived).** `scripts/header_delta.py` diffs the public `PyAPI_FUNC` / `PyAPI_DATA` declarations of the target interpreter against a committed baseline (`scripts/header_baseline_314.json`, regenerated with `--write-baseline`) and classifies every symbol the target *adds* as:

- **linked** — referenced in `src/picop/**` or `examples/cimport_ext/**`;
- **ledger** — listed in `scripts/header_ledger.json` with a mechanism reason (`skip` = indexed, no demand; `rejected` = volatile/internal/undocumented);
- **unaccounted** — neither, which is a CI failure under `--fail-on-unaccounted`.

```bash
python scripts/header_delta.py --baseline scripts/header_baseline_314.json --fail-on-unaccounted
```

The job runs on 3.15 in `picop-smoke.yml` and in `scripts/release.sh` preflight (override the target interpreter with `PYTHON315=…`, and the baseline with `HEADER_BASELINE=…`). Deprecated declarations are skipped, `internal/` headers are never scanned, and `--include DIR` points the scan at an unpacked CPython source tree when the running interpreter is not the target.

Current scan (CPython 3.14.7 baseline → 3.15.2 stable headers, 2026-11-16):

| item | count |
|------|-------|
| public declarations in 3.15.2 | **1417** |
| baseline (3.14.7) | **1367** |
| added in 3.15 | **65** |
| linked by picop | **32** |
| ledger-listed (indexed or rejected) | **34** (one overlap: `Py_SIZE`) |
| unaccounted | **0** |
| removed since 3.14 | **15** |
| removed but still referenced by picop | **0** |

The prose tables below are the human-readable annotation of that classification; `scripts/header_ledger.json` is the machine version.

## New public API — promotable

| API | Symbol(s) | Verdict | Next action |
|-----|-----------|---------|-------------|
| BytesWriter public writer API (new in 3.15, PEP 782) | `PyBytesWriter_Create`, `WriteBytes`, `Resize`, `Finish`, `Discard` | **Order 075** (extends 002) — shipped | `BytesWriter(max_size)` honours the hint on 3.15+ via `Create(hint)` + `Resize(0)` (Resize sets the logical size, so rewinding to 0 keeps the allocation as reserved capacity) |
| Public tuple builder | `PyTuple_FromArray` | **Order 076** (extends 001) — shipped | `tuple_from_array` cimport helper; loop fallback pre-3.15 |
| Interpreter view / guard (free-threading-safe thread state) | `PyInterpreterView_FromCurrent/FromMain/Close`, `PyInterpreterGuard_FromCurrent/FromView/Close`, `PyThreadState_Ensure/EnsureFromView/Release` | **Order 077** (extends 012) — shipped | `interpreter_guard()` CM + `guards_supported()` public; raw helpers cimport-only, GILState fallback pre-3.15 |
| Immortal set | `PyUnstable_SetImmortal` | **Order 078** (extends 028) — shipped | `ref_set_immortal` cimport helper; 3.14 refcount-pin emulation |
| Lazy-import mode | `PyImport_Get/SetLazyImportsMode/Filter`, `PyLazyImport_Type` | **Order 079** (extends 068) — shipped | public mode probe/get/set; filters cimport-only; `PyLazyImport_Type` rejected (internal header) |
| BytesWriter getters / low-level growth | `GetSize`, `GetData`, `GrowAndUpdatePointer`, `FinishWithSize` | **Order 080** (extends 002) — shipped | public `size()`; cimport-only `grow()` / `data()` / `finish_with_size()`; `Grow` and `FinishWithPointer` indexed, `Format` rejected |

## New public API — indexed, no demand

| API | Why not wrapped |
|-----|-----------------|
| `PyArg_ParseArray(AndKeywords)` | Argument-parsing convenience; picop's niche is hot accessors, not arg-parsing |
| `PyModule_Exec`, `PyModule_FromSlotsAndSpec`, `PyModule_GetStateSize`, `PyType_FromSlots`, `PyABIInfo` / `PyABIInfo_Check`, `PyImport_CreateModuleFromInitfunc`, `PyModule_GetToken` | Extension-authoring scaffolding; high churn, low call-site demand |
| `*_DuringGC` accessors (`PyModule_GetState_DuringGC`, `PyType_GetModule_DuringGC`, `PyObject_GetItemData_DuringGC`, `PyObject_GetTypeData_DuringGC`, `PyType_GetModuleState_DuringGC`, `PyType_GetBaseByToken_DuringGC`, `PyType_GetModuleByToken(_DuringGC)`) | Valid only inside GC traversal context; niche for picop consumers |
| `PyObject_Dump`, `PyUnstable_DumpTraceback`, `PyUnstable_DumpTracebackThreads` | Debug aids; no benchmarkable win |
| `PyExc_ImportCycleError` | picop wraps no exception-type constants; available natively to consumers |
| `Py_IS_TYPE`, `Py_SIZE`, `Py_SET_SIZE` | Now public macros — already used internally by picop, no wrapper needed |
| `PyFrozenDict_Type` | Type object; `cyfrozendict_shim.h` uses the version-guarded check helpers, no wrapper needed |

## New internals — REJECTED (volatility)

`_PyJit*` / `_PyUOpInstruction` / `_Py_Specialize_*` (JIT executor internals, change per release), `_PyDictKeys_*` / `_PyDict_InsertSplitValue` / `_PyDict_*_LockHeld` (dict keys-split internals, no ABI contract), `_PyFrame_*` / `_PyStackRef*` / `_PyThreadState_PushFrame` (frame/stackref rewrite, version-coupled), `_PyCompactLong_*` (renamed from `_PyLong_*`, private), `_PyCode_GetTLBC` / `_PyCode_InitAddressRange` (code address-range tables), `_PySlotIterator_*`, `_PyUOpsAbstractFrame`, `_PyEval_UnpackIndices`, `_PyInterpreterState_IsSpecializationEnabled`, `_PyInterpreterState_SetEvalFrameAllowSpecialization`, `_PyStats_GetLocal`, `_Py_InitializeMain`. All fail the "non-static, stable enough to link" test for public wrappers; Tier B call sites keep using the object APIs.

## Removed in 3.15 — picop exposure

| Removed | picop status |
|---------|--------------|
| `_PyBytesWriter_Init/Alloc/Prepare/Resize/Finish/Dealloc/WriteBytes` | Already guarded: shim mirrors these only under `#if PY_VERSION_HEX < 0x030F0000` (Order 074); 3.15 uses the public API. CI green |
| `PyWeakref_GetObject`, legacy `PyUnicode_As*Codec*`, `Py_Get*` (program paths), `PySys_ResetWarnOptions`, `PyImport_ImportModuleNoBlock` | Never wrapped |
| `_PyLong_Add/Multiply/Subtract`, `_PyTuple_FromArray`, `_PyCode_ConstantKey`, `_PyDict_MergeEx`, `_PyTime_AsLong/FromLong`, `_PyObject_Dump`, `_PyObject_SetManagedDict`, `_PyByteArray_empty_string`, `_Py_ReachedRecursionLimitWithMargin`, `_Py_stats` | Never wrapped |

`header_delta.py --baseline` reports `removed_referenced=0`: nothing in `src/picop/**` references a symbol the target no longer declares.

## Queue

| Order | Item | Status |
|-------|------|--------|
| 080 | BytesWriter getters / `Grow` (002) | shipped |
| 081 | `cypicklebuf` 3.14 guard removal (066) | shipped |
| 084 | Stable 3.15 toolchain: drop prerelease opt-ins | pending |
| 085 | Tier B (Cython cdef-loop) parity in CI | pending |
| 086 | `scripts/header_delta.py` — machine-derived inventory | shipped by this Order |

## Notes from the manual scans (2026-11-12 / 2026-11-13)

These are the findings the scanner now reproduces; they are kept for the mechanism reasoning the ledger entries cite.

1. **`PyBytesWriter` is entirely new in 3.15 (PEP 782), not an extension of an existing writer.** `grep PyBytesWriter_` over the 3.14.7 tree returns zero hits; picop's 3.14 path mirrors the internal `_PyBytesWriter` struct.
2. **`PyBytesWriter_Resize` semantics.** It resizes the writer to `size` bytes (grow or shrink; newly allocated bytes uninitialized) — it sets the *logical* size, it is not a pure reservation. Order 075's shipped trick is `Create(hint)` + `Resize(0)`: allocate with the hint, rewind the size. `Grow(writer, n)` adds `n` to the current size (may be negative).
3. **`PyDict_SetDefaultRef`** is not new as a symbol (present in 3.14); it is merely promoted to the Limited API in 3.15. picop already links it.
4. **`PyObject_Dump`** (3.15) replaces the deprecated `_PyObject_Dump`; `_PyObject_GetAttrId` is now `Py_DEPRECATED(3.15)`; `_PyBytes_Join` / `_PyBytes_Resize` are soft-deprecated in favour of the writer API. No picop code touches any of them.
5. **`PyPickleBuffer_*` is not 3.15-only.** `cpython/picklebufobject.h` declares `FromObject`, `GetBuffer`, `Release` and the `Check` macro in 3.14.7 as well, and the 3.14.7 binary exports all of them. Order 066's shim guard (`PY_VERSION_HEX >= 0x030F0000`) was therefore wrong; Order 081 removed it.

Negative checks: `PyModule_GetSlots` and `PyModule_GetWarningsModule` are declared nowhere in 3.15; `_PyStructSequence_NewType` stays internal (`internal/pycore_structseq.h`). Everything else in the delta is token- or GC-traversal-gated, embedding-only, debug-only, or already mirrored by an existing helper.
