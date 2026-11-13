# Changelog

## [Unreleased]

### Added
- **`cytuple` `tuple_from_array` (Order 076):** cimport-only builder over CPython 3.15+ public `PyTuple_FromArray`, with an equivalent `PyTuple_New` + INCREF-loop fallback on 3.8-3.14. Beats the idiomatic `cdef` `tnew`+`tset` fill (0.83x on 3.14, 0.94x on 3.15); a literal tuple display still wins when the items are known inline.
- **`cythread` interpreter guards (Order 077):** PEP 788 `PyInterpreterGuard`/`PyInterpreterView`/`PyThreadState_Ensure/Release` wrappers. Public `interpreter_guard()` context manager and `guards_supported()` probe on CPython 3.15+ (raw helpers cimport-only); on 3.8-3.14 `interpreter_guard()` raises `RuntimeError` and the ensure/release helpers fall back to `PyGILState_Ensure/Release`. Guard acquire costs ~6x a cached GILState check — a finalization-safety tool, not a micro-opt. Example: [`examples/pyinterpreter_guard.py`](examples/pyinterpreter_guard.py).

### Changed
- **`cybytes` `BytesWriter` (Order 075):** the `max_size` capacity hint is now honoured on CPython 3.15+ via `PyBytesWriter_Create(hint)` + `PyBytesWriter_Resize(writer, 0)` (previously ignored there; 3.8-3.14 behaviour unchanged).

## [3.8.0] — 2026-11-12 — Incremental str/bytes writers

### Added
- **`cyunicode` `UnicodeWriter` (Order 073):** incremental `str` builder over CPython 3.11+ `PyUnicodeWriter` (`write` / `write_char` / `write_ascii` / `write_repr` / `write_substring` / `write_utf8` / `finish` / `discard`, context-manager). Streaming loops beat `s += p` by ~25% with O(1) extra memory; `''.join` still wins when parts are materialized (crossover documented in PERF_PARITY). Example: [`examples/pyunicode_writer.py`](examples/pyunicode_writer.py).
- **`cybytes` `BytesWriter` (Order 074):** incremental `bytes` builder — public `PyBytesWriter` API on CPython 3.15+, internal `_PyBytesWriter` mirror on 3.8-3.14. Beats `bytearray` accumulation (0.85x) and `b += p` (0.02x); a `cdef`-level writer loop is ~5x faster than append+join. Loses to `b''.join` when parts are already materialized (3.32x) — a streaming builder, not a join replacement. Strict `finish()`/`discard()` lifecycle with context-manager support. Example: [`examples/pybytes_writer.py`](examples/pybytes_writer.py).


## [3.7.0] — 2026-11-12 — Dict lifecycle watchers

### Added
- **`cydict` watchers (Order 072):** cimport-only `dict_add_watcher` / `dict_clear_watcher` / `dict_watch` / `dict_unwatch` over CPython 3.12+ dict lifecycle callbacks (`ADDED`, `MODIFIED`, `DELETED`, `CLONED`, `CLEARED`, `DEALLOCATED`), plus the `PyDict_WatchEvent` enum and `PyDict_WatchCallback` type so a Cython callback matches the C signature. Tier B measures watcher dispatch at ~1% of an unwatched set loop; recipe: [`examples/cython/dict_watchers.md`](examples/cython/dict_watchers.md).


## [3.6.0] — 2026-11-11 — Sys helpers, critical sections, and function watchers

### Added
- **`cysys` (Order 068):** add borrowed sys attribute and `-X` getters, CPython 3.15 required/optional attribute lookup, and cimport-only mutation/stream primitives.
- **`cycriticalsection` (Order 070):** add cimport-only `cs_begin` / `cs_end` / `cs2_*` critical-section wrappers over caller-provided stack buffers plus a `critical_sections_enabled()` build query, for sections Cython's `with cython.critical_section(...)` syntax cannot express.
- **`cyfunction` watchers (Order 071):** add cimport-only `func_add_watcher` / `func_clear_watcher` over CPython's per-interpreter function lifecycle callbacks (`CREATE`, `DESTROY`, `MODIFY_CODE`, `MODIFY_DEFAULTS`, `MODIFY_KWDEFAULTS`), the `PyFunction_WatchEvent` / `PyFunctionObject` types so a Cython callback matches the C signature, and `func_event_modify_qualname()`, which reports the 3.15-only `MODIFY_QUALNAME` event id or `-1` on 3.14.


## [3.5.0] — 2026-11-10 — Warning dispatch, PickleBuffer helpers, and C-function accessors

### Added

- **`cywarnings` (Order 065):** expose CPython warning dispatch (`warn_ex`, `warn_explicit`) and warnings-module lookup, preserving active filters and exceptions.
- **`cypicklebuf` (Order 066):** add PickleBuffer construction, release, exact-type
  check, type accessor, and cimport-only raw buffer pointer access. The borrowed pointer
  is tied to the owner's unreleased lifetime; no GetObj or CheckExact exists in the
  CPython 3.15 header.
- **`cyfunction` (Order 067):** public `func_new_with_qualname`,
  `func_get_kw_defaults`, `func_set_kw_defaults`, `func_get_annotations`,
  `func_set_annotations`, and cimport-only `func_get_code_unchecked`,
  `func_get_globals_unchecked`, `func_get_module_unchecked`,
  `func_get_defaults_unchecked`, `func_get_kw_defaults_unchecked`,
  `func_get_annotations_unchecked`, `func_get_closure_unchecked`. Tier A
  measures 0.40–0.63x on the checked getters against `getattr`/`setattr` on the
  function object.
- **`cymethod` (Order 067):** public `cfunction_check`, `cfunction_check_exact`,
  `cfunction_get_self`, `cmethod_check`, `cmethod_check_exact`, `classmethod_new`,
  `staticmethod_new`, and cimport-only `cfunction_get_self_unchecked`,
  `cfunction_get_flags_unchecked`, `cfunction_get_class_unchecked`,
  `cfunction_get_function_unchecked`. `cfunction_check` is a `PyObject_TypeCheck`
  so a `PyCMethod` (a subtype of `PyCFunction`) passes it while
  `cfunction_check_exact` does not; `cfunction_get_self` promotes the borrowed
  `m_self` inside a critical section and preserves CPython's `SystemError` for
  non-C-function arguments. Tier A 0.43–0.90x, Tier B 7/7 wins (mean 0.19x).
- **`cydescr` (Order 069):** add checked `descr_name` and `descr_objclass` descriptor metadata accessors. CPython descriptor constructors and member access remain cimport-only because their raw tables/addresses require caller-managed lifetime and safety; unsafe `PyWrapper_New` is not exported.

### Fixed

- **`cyhash` wheel builds on Windows:** `hash_buffer` advanced the exported buffer with
  `void *` arithmetic, which MSVC rejects (`error C2036: 'const void *': unknown size`);
  the offset is now applied through `const char *`. GCC/clang behaviour is unchanged.

## [3.4.0] — 2026-11-10 — Buffer hashing and PEP 670 monitoring scopes

### Added

- **Free-threading coverage:** `tests/test_freethreading_stress.py` races 12 threads
  against the borrowed-result helpers (`dict_get_ref`, `dict_setdefault`,
  `dict_setdefault_ref`, `cell_get`, `list_get`, `list_get_checked`) and fails on any
  torn or lost update; the barrel smoke now runs an 8-thread `PyMutex` contention
  check (`demo.check_lock_contention()`), so `cylock` is proven under real contention
  instead of a single-threaded lock/unlock.
- **CI:** `.github/workflows/perf-parity.yml` re-measures every public helper against
  its plain-Python builtin on CPython 3.14, 3.15 and both free-threaded builds each
  week, and `scripts/perf_parity_drift.py` fails the job when those measurements
  contradict `docs/PERF_PARITY.md`. The tables here and the parity notes in the `.pyi`
  stubs are regenerated from one fresh pass.
- **`cymonitoring` (Order 062):** cimport-only PEP 670 helpers:
  `monitoring_scope`, `monitoring_exit_scope`, `monitoring_active`,
  `monitoring_is_instrumented`, and the 17 `fire_*` helpers, plus the 18
  `PY_MONITORING_EVENT_*` constants and `PyMonitoringState`.
- **`cyhash` (Order 064):** add public `hash_buffer(data, start=0, end=-1)` plus
  cimport-only `hash_buffer_raw`, `hash_pointer`, and `hash_generic`. Tier A measures
  0.40–0.78x on `bytearray`, `array.array`, and buffer ranges, where the only pure-Python
  route is `hash(bytes(data))`; the builtin stays cheaper for `bytes` and `memoryview`,
  which cache the hash on the object.
- **Build/infra:** `picop` now builds prebuilt wheels. `[tool.cibuildwheel]` in
  `pyproject.toml` targets CPython 3.14/3.15 and the free-threaded `cp314t`/`cp315t`
  tags on manylinux, macOS (universal2) and Windows, and runs the test suite inside
  each build container. `publish.yml` uploads those wheels with the sdist on every
  `picop-v*` tag; `wheels.yml` builds the Linux x86_64 subset on every push to `main`
  and every pull request as a compile check.

### Changed

- **Build/infra:** `setup.py` uses MSVC-compatible flags on Windows (`-O2 -utf-8`)
  instead of the GCC-only `-Wno-*` warnings, so the wheel builds compile with `cl.exe`.
- **Build/infra:** the UUID entropy source no longer links OpenSSL. `c_uuid4` fills
  its thread-local buffer from the operating system CSPRNG (`BCryptGenRandom` on
  Windows, `/dev/urandom` elsewhere) through `src/picop/uuid/entropy.c`, so a source
  install needs a C toolchain only. `libssl-dev` is dropped from the CI workflows and
  the README install note. No public surface changes.
- **cimport coverage:** `examples/cimport_ext/demo.pyx` now exercises every
  cimport-only module — `cyerr`, `cymem`, `cythread`, `cyatomic`, `cyref`,
  `cygetargs`, `cyceval`, `cypystate`, `cypylifecycle`, `cypyport`, `cyversion`,
  `cylongintrepr` (plus the existing `cylock`, `cycode`, `cyframe`,
  `cytraceback`, `cymemoryview`, UUID checks) — and `scripts/smoke_barrel_cimport.sh`
  asserts each result on the smoke matrix.
- **CI gates:** `picop-docs.yml` now runs `scripts/grade_trackers.py`, and
  `scripts/release.sh` takes its interpreter from `PYTHON` instead of hard-coding
  `python3` (the preflight checks failed when the active interpreter had no picop).
  `tmp/` is ignored.

### Fixed

- **`cyerr.err_no_memory()`** is now `void`. `PyErr_NoMemory` raises `MemoryError`
  and returns NULL, so the old `PyObject *` wrapper returned NULL and Cython turned
  that into an unraisable exception in every caller. Use the helper for its side
  effect, then check `err_occurred()`.
- **UUID buffer asserts under MSVC:** `src/picop/uuid/uuid.h` uses a portable
  `_Static_assert` fallback (negative-size typedef), because MSVC ignores
  `-std=c11` and its default C mode rejects `_Static_assert`; `setup.py` no longer
  passes `-std=c11` on Windows. `tests/test_uuid_entropy.py` raises its C-compile
  subprocess timeout from 30 s to 120 s so the cross-arch wheel test on macOS
  runners does not fail on a cold clang start.
- **Windows entropy provider:** `src/picop/uuid/entropy.c` includes `<windows.h>`
  before `<bcrypt.h>`; MSVC rejects `bcrypt.h` standalone (`ULONG`, `BCRYPT_HANDLE`
  and friends come from the Windows base headers).
- **Windows build flags:** `setup.py` passes `/std:c11` to MSVC (the `cyatomic`
  shim needs `<stdatomic.h>` and `_Atomic`, which MSVC only enables in C11 mode)
  and no longer sends the GCC-only `-std=c11` to `cl.exe`.
- **Portable bytes search:** the `cybytearray` containment helper used glibc-only
  `memmem()`, which MSVC and MinGW do not provide (link error: 1 unresolved
  external). It now uses `cy_memmem()` from `src/picop/cybytes_shim.h`, a
  `memchr` + `memcmp` scan with the same semantics.

## [3.3.0] — 2026-11-06 — PyMutex cimport helpers and perf-parity gates

### Added

- `cylock`: cimport-only `PyMutex` helpers (`mutex_init`, `mutex_lock`,
  `mutex_unlock`, `mutex_is_locked`) for free-threaded extensions that need a
  typed mutex outside `cython.critical_section`. No Python-visible surface; the
  barrel cimport (`from picop cimport PyMutex, mutex_lock, …`) is exercised by the
  out-of-tree smoke.
- `docs/PERF_PARITY.md` and `scripts/perf_parity_report.py`: a machine-generated table
  of the public helpers that are **slower** than the plain-Python builtin in every Tier A
  case, plus the case-dependent ones, with the builtin to use instead.
- Every Tier-A-losing public helper now has a `.pyi` stub with a
  `Slower than the plain-Python equivalent …` docstring note (46 stub entries added for
  helpers that were `cpdef` but undocumented).
- `scripts/ops_inventory_coverage.py --strict` now cross-checks that table against the
  `.pyi` docstrings in both directions, and runs in the smoke workflow.

## [3.2.0] — 2026-11-05 — Frame, code, and traceback accessors with refcount-balanced getters

### Added

- `cyframe`: add 11 public frame readers and two cimport-only helpers for frame
  construction and entry-frame detection. The same API is available on CPython
  3.14 and 3.15; `frame_locals` preserves the PEP 667 proxy, and missing
  `frame_var` names raise `NameError`.
- `cycode`: add 15 public code-object readers and two cimport-only helpers on CPython
  3.11+; adaptive `co_code` is version-sensitive, and `code_eq` remains rejected in
  favor of identity via `obj_eq`.
- `cytraceback`: add public traceback helpers `tb_check`, `tb_next`, `tb_frame`,
  `tb_lineno`, `tb_lasti`, and `tb_depth`; `tb_next_borrow` is cimport-only.

### Fixes

- `cycall`, `cyframe`, `cycode`: new-reference C getters (`PyObject_Vectorcall`,
  `PyFrame_GetCode` / `GetBack` / `GetGenerator` / `GetVar` / `GetVarString` /
  `PyFrame_New`, and the `cycode_shim.h` field readers) were declared as `PyObject *`
  and returned through an `<object>` cast, which incref'd a reference Cython already
  owned — one leaked object per call. They now hand the reference straight to Cython
  (or convert and `Py_DECREF`). Pinned by
  `test_object_getters_hand_back_exactly_one_reference` in `tests/test_systems.py`.
- `cycellobject`: `cell_get_unchecked` declared the *borrowed* `PyCell_GET` macro as
  `object`, which dropped the cell contents' refcount by one per call. The macro is now
  declared `PyObject *` and promoted with an `<object>` cast inside the same critical
  section.
- Ownership convention recorded in [`docs/SAFETY.md`](docs/SAFETY.md).

## [3.1.0] — 2026-11-05 — CPython 3.15 sentinel, frozendict, and vectorcall helpers

- `cysentinel`: add CPython 3.15 sentinel checks and constructors. On Python 3.14,
  checks return `False` and constructors raise `NotImplementedError`.
- `cyfrozendict`: add the CPython 3.15 `frozendict` surface — `frozendict_check`,
  `frozendict_check_exact`, `frozendict_new`, `frozendict_empty`, plus the
  dict-or-frozendict gates `anydict_check` / `anydict_check_exact` and the
  shared-layout reader `anydict_len`. On Python 3.14 the checks return `False`
  and the constructors raise `NotImplementedError` instead of silently
  returning a mutable `dict`. `frozendict_new` on an existing frozendict is a
  refcount bump, not a copy — build from an iterable for a new object.
  Bench tables in [`docs/modules/057_cyfrozendict.md`](docs/modules/057_cyfrozendict.md);
  examples in [`examples/pyfrozendict.py`](examples/pyfrozendict.py).
- `cycall`: add the cimport-only bound-method helpers `call_method_noargs`,
  `call_method_onearg`, `call_method_vector` and the `PyVectorcall_NARGS` wrapper
  `vectorcall_nargs`; document that `call_vector` forwards `nargsf` unchanged
  (reserved-slot offset bit allowed) and that `kwnames` must be `NULL` or a
  tuple — `Py_None` is undefined and was measured to crash with SIGSEGV.
- Add the Tier B call harness `bench/tier_b/cycall.py` (picop `cdef` helpers vs
  typed Cython baselines) with correctness/depth probes; measured tables are in
  [`docs/modules/056_cycall.md`](docs/modules/056_cycall.md). No public helper
  changed behaviour and the frozen Core is untouched.

## [3.0.0] — 2026-10-18 — picop 3.0 — picop-only imports

- Promote the 3.0 release candidate to stable: Python imports and Cython cimports use `picop` only. The `cypy` compatibility package is gone; rebuild downstream Cython extensions.
- Retain the RC1 native implementation, UUID behavior and Python 3.14/3.15 plus genuine GIL-disabled 3.14t/3.15t support.
- Validate the existing Swissquote Cython market-data decoder against RC1 on all four ABIs: 13 offline tests per ABI plus a 1,000-frame/9,000-row workload. Its own extension enables the GIL by default; picop does not. Forced-no-GIL consumer tests passed but do not declare downstream threading support.
- Complete Tier A benchmark scenarios for the three call helpers and eight buffer/memoryview metadata helpers; coverage does not imply a performance approval or change the frozen Core.
- Add explicit UUID benchmark reference selection (`--baseline`) and a separately recorded native-implementation reference for the i7-6700 / CPython 3.15.0rc2 host. Preserve the historical baseline, result schema and 25% regression budget.

## [3.0.0rc1] — 2026-10-18 — picop 3.0 RC1 — picop-only imports

- Make CPython 3.15 primary while retaining 3.14 and genuine GIL-disabled 3.14t/3.15t operation. Require Cython 3.3 or newer and separate builds for each ABI.
- Replace removed weakref APIs with `PyWeakref_GetRef`, balance strong references, and protect mutable container/function/cell access against concurrent replacement. Invalid weakref arguments propagate the strong-reference API's `TypeError`.
- Repair stealing bytes concat/resize ownership, mutable bytearray/array comparisons, memoryview export lifetimes and ANSI initialization.
- Replace UUID's fabricated MRO with a real final native `uuid.UUID` subtype. Eagerly initialize its stdlib integer slot, preserve typed factories and Python value behavior, reject reinitialization, and remove private lazy caches/layout fields. Downstream Cython extensions must rebuild; no old private binary layout is preserved.
- Speed up UUID integer construction using the public `PyLongWriter` API on compatible layouts and remove redundant Cython factory reference transfers, preserving eager stdlib slots and genuine no-GIL behavior.
- Reject undersized UUID entropy buffers at build time and fail import if fork-child entropy invalidation cannot be registered.
- Remove the `cypy` Python package and Cython cimport shims. Migrate Python imports and cimports (including UUID direct/barrel cimports) to `picop`; rebuild downstream Cython extensions. No compatibility shim is provided. This is a release candidate, not stable 3.0.
- Move the standalone project from `packages/picop/` to the repository root. Build, install, test, documentation and release commands now run from the root; CI and release paths follow the new layout. Python imports and Cython cimports use `picop`.
- Fix `obj_call`'s default no-keyword path so `None` is not passed as a C keyword dictionary; preserve callback results and exceptions without adding an empty-dict allocation.
- Migrate benchmark runners, generated Cython harnesses and inventory tooling to `picop`; repair stale string-helper names and the file benchmark's exhausted input fixture. Existing measured baselines and result schemas are unchanged.

## [2.1.0] — 2026-09-06 — systems call and buffer helpers

- Add `cycall` zero-, one-, and two-argument CPython call helpers, including a cimport-only vectorcall primitive.
- Add public buffer and memoryview metadata inspection helpers.
- Prefer `cyerr` raised-exception get/set lifecycle helpers on Python 3.14+.

## [2.0.0] — 2026-08-06 — rename import package to picop (soft cypy alias)

- Move implementation tree to `src/picop/` (preferred import: `from picop…` / `from picop… cimport`).
- Keep `src/cypy/` as a soft shim: re-exports `picop`, emits `DeprecationWarning` on import; Cython `cimport` shims mirror the same surface.
- PyPI distribution name was already **`picop`** (`pip install picop`); version **2.0.0**.
- Fix `cyceval` cimport helper: `PyEval_ThreadsInitialized` removed on 3.14 — `eval_threads_initialized` always returns true so barrel cimport builds.
- **3.0 plan:** remove the `cypy` import package and cimport shims entirely — migrate call sites to `picop` before then.

## [1.44.16] — 2026-08-06 — PyPI name `picop` + publish CI

- PyPI distribution name is **`picop`** (`pip install picop`); import package remains **`cypy`**.
- Add Trusted Publishing workflow [`.github/workflows/publish.yml`](.github/workflows/publish.yml) (tag `v*` → PyPI; manual → TestPyPI/PyPI).
- Publish **sdist only** (PyPI rejects untagged `linux_x86_64` wheels; manylinux via cibuildwheel is follow-up).

## [1.44.15] — 2026-08-02 — expand pytest suite beyond UUID

- Add focused pytest modules for `cypy.hot`, Core containers, `cypy.protocols`, export gates, and example ``main()`` smokes (no API change).

## [1.44.14] — 2026-08-02 — stub-hide Tier A losers in `cytype`

- Omit ``type_is_subtype`` from `cytype.pyi` (Tier A `>1.02x`; still `cpdef`).

## [1.44.13] — 2026-08-02 — stub-hide Tier A losers in `cytime`

- Omit ``time_wall`` from `cytime.pyi` (Tier A `>1.02x`; still `cpdef`).

## [1.44.12] — 2026-08-02 — stub-hide Tier A losers in `cyset`

- Omit ``set_pop`` from `cyset.pyi` (Tier A `>1.02x`; still `cpdef`).

## [1.44.11] — 2026-08-02 — stub-hide Tier A losers in `cymethod`

- Omit ``method_new`` from `cymethod.pyi` (Tier A `>1.02x`; still `cpdef`).

## [1.44.10] — 2026-08-02 — stub-hide Tier A losers in `cyiterator`

- Omit ``iter_next`` from `cyiterator.pyi` (Tier A `>1.02x`; still `cpdef`).

## [1.44.9] — 2026-08-02 — stub-hide Tier A losers in `cycodecs`

- Omit ``codec_encode``, ``codec_decode`` from `cycodecs.pyi` (Tier A `>1.02x`; still `cpdef`).

## [1.44.8] — 2026-08-02 — stub-hide Tier A losers in `cyiterobject`

- Omit ``seqiter_new``, ``calliter_new`` from `cyiterobject.pyi` (Tier A `>1.02x`; still `cpdef`).

## [1.44.7] — 2026-08-02 — stub-hide Tier A losers in `cyfloat`

- Omit ``float_from_double``, ``float_from_cstr``, ``float_as_double`` from `cyfloat.pyi` (Tier A `>1.02x`; still `cpdef`).

## [1.44.6] — 2026-08-02 — stub-hide Tier A losers in `cylong`

- Omit ``long_from_long``, ``long_from_ssize``, ``long_from_double``, ``long_as_long``, ``long_as_ssize``, ``long_as_double`` from `cylong.pyi` (Tier A `>1.02x`; still `cpdef`).

## [1.44.5] — 2026-08-02 — stub-hide Tier A losers in `cymapping`

- Omit `map_len` from `cymapping.pyi` / `cypy.protocols` (Tier A `>1.02x` vs `len`).

## [1.44.4] — 2026-08-02 — stub-hide Tier A losers in `cysequence`

- Omit `seq_len` / `seq_size` / `seq_count` from `cysequence.pyi` (Tier A `>1.02x`).
- Drop `seq_len` / `seq_size` from `cypy.protocols`; keep winning sequence helpers stubbed.

## [1.44.3] — 2026-08-02 — stub-hide Tier A losers in `cynumber`

- Omit measured Tier A losers from `cynumber.pyi` (`num_add` / `mul` / `neg` / …).
- Keep stubbed: `num_check*` / `num_eq` / `num_floordiv` / `num_inplace_add` (+ unmeasured siblings).

## [1.44.2] — 2026-08-02 — stub-hide Tier A losers in `cyobject`

- Omit Tier A losers (`ratio > 1.02` vs builtins) from `cyobject.pyi`
  (`obj_hasattr` / `getattr` / `type` / `len` / …); keep `cpdef` for Cython.
- Keep stubbed equality winners: `obj_richcompare`, `obj_richcompare_bool`, `obj_eq`.
- Drop `obj_len` / `obj_size` from `cypy.protocols`; example smoke uses equality helpers.

## [1.44.1] — 2026-08-01 — GCC 14 / 3.14 pxd compile fixes

- Declare `_PySet_Update` via a local prototype in `cyset.pxd` (exported from
  libpython but absent from public `Python.h` on 3.14).
- Type `PyType_*` externs as `type` / `unsigned long` in `cytype.pxd` and cast
  at call sites so GCC 14+ does not reject `PyObject*` vs `PyTypeObject*`.

## [1.44.0] — 2026-07-23 — C-backed UUID values and generation

- Move the optimized UUID implementation from Cycel into `cypy.uuid`.
- Add `UUID`, `uuid4()`, and `uuid4_bytes()` to the Python and Cython package
  barrels while retaining stdlib `uuid.UUID` interoperability.
- Preserve thread-local buffered OpenSSL entropy, fork reset behavior, type
  declarations, benchmarks, and CPython 3.14t compatibility coverage.
- Carry the upstream asyncpg attribution and Apache-2.0 terms for the
  adapted UUID portions; cypy remains MIT as a whole.

## [1.43.1] — 2026-07-22 — package-barrel `from cypy cimport` fix

- Drop unused wchar `Py_Get/SetProgramName` externs from `cypylifecycle.pxd` (undeclared `wchar_t` broke `__init__.pxd` re-exports).
- Remove `nogil` from `thread_get_ident` (Cython marks `PyThread_get_thread_ident` as GIL-requiring).
- Fix `longrepr_digits` for Python 3.14 `long_value.ob_digit` layout (barrel consumers compile all inlined pxds).
- Add out-of-tree smoke: `examples/cimport_ext/` + `scripts/smoke_barrel_cimport.sh`.

All notable changes to `cypy` are documented here. Version from
[`src/cypy/__about__.py`](src/cypy/__about__.py).

## [1.43.0] — 2026-07-22 — full public-ops inventory (Tier A + rollups)

### Docs / benches

- Close public-barrel coverage: ``cystr_order`` / ``cyaccessors`` / ``cyruntime``
  inventory harnesses (+ ``cystr_order`` Tier B). ``OPS_INVENTORY.md`` now
  **0 pending** (427 compares / 11 explicit ``n/a``). Rollup:
  ``docs/OPS_INVENTORY_TIERB.md``. Coverage gate:
  ``python3.14 scripts/ops_inventory_coverage.py --strict``.
- Notable: ``str_cmp`` Tier B **0.26x**; ``conv_strnicmp`` Tier A **~0.27x**;
  honest loses include ``mod_import_object`` (~2x) and ``codec_strict_errors``
  (exception path). Stale “leave off hot until measured” tracker notes refreshed.

## [1.42.5] — 2026-07-22 — ne/search ops inventory (Tier A+B)

### Docs / benches

- ``bench/cyne_search_inventory_bench.py`` + Tier B ``bench/tier_b/cyne_search*`` for
  ``bytes_ne`` / ``bytes_startswith`` / ``bytes_endswith``, ``bytearray_ne`` /
  ``bytearray_contains``, ``array_ne``, ``memoryview_ne``. All gate-pass Tier A;
  Tier B wins (notably ``bytearray_contains`` **0.24x**, ``memoryview_ne`` 1KiB
  Tier A **0.02x** vs slow Python). Tracker paste + ``OPS_INVENTORY`` → ``tierB``.

## [1.42.4] — 2026-07-22 — public ops inventory coverage foundation

### Docs / tooling

- Add ``scripts/ops_inventory_coverage.py``: public ``cy*`` barrel vs
  ``session.compare`` labels in ``bench/**``; checklist in
  ``docs/OPS_INVENTORY.md`` (seed: covered → ``tierA``/``tierB``, gaps →
  ``pending``). Link from ``docs/README.md``.

## [1.42.3] — 2026-07-22 — full `*_eq` Tier B inventory

### Docs / benches

- Tier B depth for all **39** public ``*_eq`` helpers: cypy ``cdef`` loop vs
  typed Cython ``==`` baseline (``bench/tier_b/cyeq_inventory.py`` +
  ``cyeq_{containers,buffers,scalars,misc}_tb.pyx``).
- Rollup: ``docs/EQ_INVENTORY_TIERB.md``; paste Tier B tables into module
  trackers (Tier A kept). Themes: identity/memcmp wins; abstract
  ``seq_eq``/``map_eq``/``buf_eq``/``num_eq`` lose in cdef loops.

## [1.42.2] — 2026-07-22 — full `*_eq` Tier A inventory

### Docs / benches

- Add ``bench/cyeq_inventory_bench.py`` covering remaining public ``*_eq``
  helpers missing from module harnesses; paste measured tables into trackers.
- ``docs/EQ_INVENTORY.md`` summary. Note: ``buf_eq`` mv↔mv **1.14x** lose
  (prefer ``memoryview_eq``).

## [1.42.1] — 2026-07-22 — eq Tier A depth pass

### Fixed / docs

- Replace smoke-placeholder ``*_eq`` tracker rows with measured Tier A
  tables (``deque_eq``, ``range_eq``, ``bytes_bytearray_eq``, ``context_eq``,
  identity misc). New harnesses: ``bench/cydeque_bench.py``,
  ``bench/cyrange_bench.py``, ``bench/cyeq_misc_bench.py``; extended
  ``cybytes`` / ``cycontextvars`` benches.

## [1.42.0] — 2026-07-22 — `context_eq` + Runtime eq stretch

### Added

- **`context_eq`** (`cycontextvars`): ``Context`` value equality — identity +
  richcompare (same as ``Context.__eq__``). Soft ``ctxeq``. On ``cypy``
  (not ``hot``). ``ContextVar`` / ``Token`` stay identity → use ``obj_eq``.
- **`docs/EQ_RUNTIME.md``**: Runtime/embedding ``*_eq`` checklist (#44) —
  skip/done; no mass identity wrappers.

## [1.41.0] — 2026-07-22 — `bytes_bytearray_eq`

### Added

- **`bytes_bytearray_eq`** (`cybytes`): cross-type ``bytes`` ↔ ``bytearray``
  content equality — identity / len + ``memcmp`` on ``AS_STRING`` (either
  order; same-type also works). Soft ``bba_eq``. On ``cypy`` /
  ``cypy.buffers`` (not ``hot``; prefer typed ``bytes_eq`` / ``bytearray_eq``
  there). Cross-link: ``buf_eq`` is buffer-protocol / views, not this.

## [1.40.0] — 2026-07-22 — `range_eq`

### Added

- **`range_eq`** (`cyrange`): ``range`` equality — identity +
  richcompare (same as ``range.__eq__``; empty / equivalent spans).
  Soft ``rqeq``. On ``cypy`` / ``cypy.containers`` (not ``hot``).

## [1.39.0] — 2026-07-22 — `deque_eq`

### Added

- **`deque_eq`** (`cydeque`): `collections.deque` equality — identity +
  richcompare (same as ``deque.__eq__``). Soft ``dqeq``. On ``cypy`` /
  ``cypy.containers`` (not ``hot``).

## [1.38.0] — 2026-07-22 — `func_eq` / `method_eq` / `mod_eq` / `gen_eq` / `iter_eq`

### Added

- **`func_eq`** (`cyfunction`): function equality via identity (``a is b``) —
  CPython ``object.__eq__``. Soft ``funceq``. On ``cypy`` (not ``hot``).
- **`method_eq`** (`cymethod`): bound-method equality via identity short-circuit
  + ``PyObject_RichCompareBool`` (``Py_EQ``) — CPython ``method_richcompare``
  (same function + ``__self__``; not identity). Soft ``methodeq``. On ``cypy``
  (not ``hot``).
- **`mod_eq`** (`cymodule`): module equality via identity (``a is b``) —
  CPython ``object.__eq__``. Soft ``modeq``. On ``cypy`` (not ``hot``).
- **`gen_eq`** (`cygenobject`): generator equality via identity (``a is b``) —
  CPython ``object.__eq__``. Soft ``geneq``. On ``cypy`` (not ``hot``).
- **`iter_eq`** (`cyiterator`): iterator equality via identity (``a is b``) —
  typical CPython ``object.__eq__``. Soft ``itereq``. On ``cypy`` (not ``hot``).

### Notes

- **`code_eq` skipped:** no ``cycode`` module (``cycodecs`` is codecs); structural
  code equality would need a dedicated module — out of scope for this batch.

## [1.37.0] — 2026-07-22 — `weakref_eq`

### Added

- **`weakref_eq`** (`cyweakref`): weakref/proxy equality via identity
  short-circuit + ``PyObject_RichCompareBool`` (``Py_EQ``) — CPython
  ``weakref_richcompare`` (referent ``==`` when both alive; identity when
  either is dead). Soft ``weakrefeq``. On ``cypy`` (not ``hot`` — Runtime;
  validate win before promoting).

## [1.36.0] — 2026-07-22 — `capsule_eq`

### Added

- **`capsule_eq`** (`cypycapsule`): capsule equality via identity (``a is b``) —
  CPython uses ``object.__eq__``; same pointer/name does not make distinct
  capsules equal. Soft ``capsuleeq``. On ``cypy`` (not ``hot`` — Runtime;
  validate win before promoting).

## [1.35.0] — 2026-07-22 — `cell_eq`

### Added

- **`cell_eq`** (`cycellobject`): cell equality via identity short-circuit +
  ``PyObject_RichCompareBool`` (``Py_EQ``) — content equality (CPython
  ``cell_richcompare``; empty↔empty True; not identity). Soft ``celleq``. On
  ``cypy`` (not ``hot`` — Runtime; validate win before promoting).

## [1.34.0] — 2026-07-22 — `type_eq`

### Added

- **`type_eq`** (`cytype`): type-object equality via identity (``a is b``) —
  CPython ``type_richcompare`` default; not Python ``==`` when a metaclass
  overrides ``__eq__``. Soft ``typeeq`` (``teq`` remains ``tuple_eq``). On
  ``cypy`` (not ``hot`` — Runtime; validate win before promoting).

## [1.33.0] — 2026-07-22 — `obj_eq`

### Added

- **`obj_eq`** (`cyobject`): generic object equality via ``PyObject_RichCompareBool``
  (``Py_EQ``) — identity short-circuit (incl. ``nan is nan`` → True; same as the
  C-API, not always Python ``==`` for floats). Prefer typed ``*_eq`` when known.
  Soft ``oeq``. On ``cypy`` / ``cypy.protocols`` (not ``hot`` — validate win
  before promoting).

## [1.32.0] — 2026-07-22 — `dt_timedelta_eq`

### Added

- **`dt_timedelta_eq`** (`cydatetime`): timedelta equality — identity short-circuit;
  exact ``timedelta`` pairs compare days/seconds/microseconds; else richcompare
  (subtypes — Python ``==`` parity). Soft ``dteq_delta``. On ``cypy`` (not
  ``hot`` — Runtime; validate win before promoting).

## [1.31.0] — 2026-07-22 — `dt_datetime_eq`

### Added

- **`dt_datetime_eq`** (`cydatetime`): datetime equality — identity short-circuit;
  exact naive ``datetime`` pairs compare year/month/day/hour/minute/second/
  microsecond; else richcompare (subtypes / aware/naive / offset / date↔datetime
  Python ``==`` parity; fold ignored). Soft ``dteq_dt``. On ``cypy`` (not
  ``hot`` — Runtime; validate win before promoting).

## [1.30.0] — 2026-07-22 — `dt_time_eq`

### Added

- **`dt_time_eq`** (`cydatetime`): time equality — identity short-circuit; exact
  naive ``time`` pairs compare hour/minute/second/microsecond; else richcompare
  (subtypes / aware/naive / offset Python ``==`` parity; fold ignored). Soft
  ``dteq_time``. On ``cypy`` (not ``hot`` — Runtime; validate win before
  promoting).

## [1.29.0] — 2026-07-22 — `dt_date_eq`

### Added

- **`dt_date_eq`** (`cydatetime`): date equality — identity short-circuit; exact
  ``date`` pairs compare year/month/day; else richcompare (subtypes /
  ``date`` vs ``datetime`` Python ``==`` parity). Soft ``dteq_date``. On
  ``cypy`` (not ``hot`` — Runtime; validate win before promoting).

## [1.28.0] — 2026-07-22 — `slice_eq`

### Added

- **`slice_eq`** (`cyslice`): slice equality — identity short-circuit +
  richcompare (same semantics as ``slice.__eq__``; compares start/stop/step
  objects, so ``None`` bounds are not normalized to ``0``/``1``). Soft ``sleq``.
  On ``cypy`` / ``cypy.buffers`` (not ``hot`` — completeness / buffer-adjacent).

## [1.27.0] — 2026-07-22 — `num_eq`

### Added

- **`num_eq`** (`cynumber`): abstract number equality via
  ``PyObject_RichCompare`` (Python ``==`` parity, including NaN != NaN even for
  the same object — not ``RichCompareBool``, which identity-shortcuts). Prefer
  typed ``long_eq`` / ``float_eq`` / ``complex_eq`` / ``bool_eq`` when known.
  Soft ``neq_num``. On ``cypy`` / ``cypy.protocols`` (not ``hot``).

## [1.26.0] — 2026-07-22 — `complex_eq`

### Added

- **`complex_eq`** (`cycomplex`): complex/value equality with Python parity
  (NaN on either real or imag => unequal even for the same object;
  ``+0.0 == -0.0`` on each part). Complex/complex uses C ``double ==`` on
  real/imag; mixed types use ``PyObject_RichCompare`` (not ``RichCompareBool``,
  which identity-shortcuts same-object NaN parts). Soft ``ceq``. On ``cypy``
  (not ``hot`` — clarity / scalar completeness).

## [1.25.0] — 2026-07-22 — `float_eq`

### Added

- **`float_eq`** (`cyfloat`): float/value equality with Python parity (NaN != NaN
  even for the same object, ``+0.0 == -0.0``). Float/float uses C ``double ==``;
  mixed types use ``PyObject_RichCompare`` (not ``RichCompareBool``, which
  identity-shortcuts NaN). Soft ``feq``. On ``cypy`` (not ``hot`` — clarity /
  scalar completeness).

## [1.24.0] — 2026-07-22 — `bool_eq`

### Added

- **`bool_eq`** (`cybool`): boolean/value equality — identity short-circuit +
  richcompare (same semantics as ``==``; True/False singletons hit identity).
  Soft ``booleq``. On ``cypy`` (not ``hot`` — clarity / scalar completeness).

## [1.23.0] — 2026-07-22 — `long_eq` / `int_eq`

### Added

- **`long_eq`** / **`int_eq`** (`cylong`): integer equality — identity short-circuit +
  richcompare (same semantics as ``==``). Preferred ``long_eq``; ``int_eq`` is a
  discoverability alias. Soft ``loeq`` / ``ieq``. On ``cypy`` (not ``hot`` —
  small-int ``==`` already specializes).

## [1.22.0] — 2026-07-22 — `map_eq`

### Added

- **`map_eq`** (`cymapping`): abstract mapping equality — identity/size
  short-circuit + richcompare (same semantics as ``==``). Soft ``mapeq``. Prefer
  typed ``dict_eq`` when known. On ``cypy`` / ``cypy.protocols``.

## [1.21.0] — 2026-07-22 — `seq_eq`

### Added

- **`seq_eq`** (`cysequence`): abstract sequence equality — identity/size
  short-circuit + richcompare (same semantics as ``==``). Soft ``sqeq``. Prefer
  typed ``list_eq`` / ``tuple_eq`` when known. On ``cypy`` / ``cypy.protocols``.

## [1.20.0] — 2026-07-22 — `frozenset_eq`

### Added

- **`frozenset_eq`** (`cyset`): typed ``frozenset`` equality — identity/size
  short-circuit + richcompare (same semantics as ``==``). Soft ``fseteq``. On
  ``cypy`` / ``cypy.containers``.

## [1.19.0] — 2026-07-22 — `set_eq`

### Added

- **`set_eq`** (`cyset`): typed ``set`` equality — identity/size short-circuit +
  richcompare (same semantics as ``==``). Soft ``seteq`` (not ``seq`` — avoids
  ``seq_*`` / ``sq*`` confusion). On ``cypy`` / ``cypy.containers``.

## [1.18.0] — 2026-07-22 — `dict_eq`

### Added

- **`dict_eq`** (`cydict`): typed ``dict`` equality — identity/size short-circuit +
  richcompare (same semantics as ``==``). Soft ``deq``. On ``cypy`` /
  ``cypy.containers``.

## [1.17.0] — 2026-07-22 — `tuple_eq`

### Added

- **`tuple_eq`** (`cytuple`): typed ``tuple`` equality — identity/len + richcompare.
  Soft ``teq``. On ``cypy`` / ``cypy.containers``.

## [1.16.0] — 2026-07-22 — `list_eq`

### Added

- **`list_eq`** (`cylist`): typed ``list`` equality — identity/len short-circuit +
  richcompare (same semantics as ``==``). Soft ``leq``. On ``cypy`` /
  ``cypy.containers``.

## [1.15.0] — 2026-07-22 — `uutf8_eq`

### Added

- **`uutf8_eq`** (`cyunicode`, **cimport-only**): compare UTF-8 byte views of two
  ``str`` via ``uutf8_and_size`` + ``memcmp`` (embedded NUL OK). Borrowed
  pointers must not outlive the arguments.

## [1.14.0] — 2026-07-22 — `str_lt` / `str_le` / `str_gt` / `str_ge`

### Added

- **`str_lt` / `str_le` / `str_gt` / `str_ge`** (`cystr`): typed ordering
  predicates via ``str_cmp``. Soft ``slt``/``sle``/``sgt``/``sge``. On ``cypy``
  (not ``hot``).

## [1.13.0] — 2026-07-22 — `str_cmp`

### Added

- **`str_cmp`** (`cystr`): three-way typed ``str`` compare → ``-1`` / ``0`` / ``1``
  via ``PyUnicode_Compare`` (identity short-circuit). Soft aliases ``str_compare`` /
  ``scmp`` (COMPAT only). On ``cypy`` (not ``hot``).

## [1.12.0] — 2026-07-22 — `unicode_eq`

### Added

- **`unicode_eq`** (`cyunicode`): discoverability alias of ``str_eq`` (same
  semantics; no divergent UCS path). Soft ``ueq``. On ``cypy``.

## [1.11.0] — 2026-07-22 — `bytes_endswith`

### Added

- **`bytes_endswith`** (`cybytes`): typed suffix test — empty suffix True,
  longer-than-`s` False, else tail `memcmp`. Soft `bendswith`. On `cypy` /
  `cypy.hot` / `cypy.buffers` (mirrors `str_endswith`).

## [1.10.0] — 2026-07-22 — `bytes_startswith`

### Added

- **`bytes_startswith`** (`cybytes`): typed prefix test — empty prefix True,
  longer-than-`s` False, else `memcmp` on `PyBytes_AS_STRING`. Soft
  `bstartswith`. On `cypy` / `cypy.hot` / `cypy.buffers` (mirrors
  `str_startswith`).

## [1.9.0] — 2026-07-22 — `bytearray_contains`

### Added

- **`bytearray_contains`** (`cybytearray`): typed `bytearray` membership for a
  `bytes` needle — same small-buffer `memchr`/`memmem` / large-buffer `in`
  hybrid as `bytes_contains`. Soft `bacontains`. On `cypy` / `cypy.hot` /
  `cypy.buffers`.

## [1.8.0] — 2026-07-22 — `buf_eq`

### Added

- **`buf_eq`** (`cybuffer`): abstract buffer-protocol equality — acquire
  `PyBUF_FULL_RO` views, format/size/shape gates, C-contiguous `memcmp` fast
  path, non-contiguous → `memoryview` richcompare. Soft alias `buffer_eq`
  (COMPAT only). On `cypy` / `cypy.buffers` (not `hot` — heavier than typed
  `bytes_eq`).

## [1.7.0] — 2026-07-22 — `bytearray_ne` / `array_ne` / `memoryview_ne`

### Added

- **`bytearray_ne`**, **`array_ne`**, **`memoryview_ne`**: typed inequality siblings of
  the corresponding `*_eq` helpers (`not *_eq` / soft `bane` / `ayne` / `mvne`).
  Same contig/format rules as `*_eq`. On `cypy` / `cypy.hot` / `cypy.buffers`
  (mirrors `bytes_ne` / `str_ne`).

## [1.6.0] — 2026-07-22 — `bytes_ne`

### Added

- **`bytes_ne`** (`cybytes`): typed `bytes` inequality (`not bytes_eq` / soft `bne`).
  On `cypy` / `cypy.hot` / `cypy.buffers` (mirrors `str_ne` API; pairs with `bytes_eq`).

## [1.5.0] — 2026-07-22 — `memoryview_eq`

### Added

- **`memoryview_eq`** (`cymemoryview`): typed `memoryview` equality — C-contiguous
  same layout/`memcmp` fast path; non-contiguous falls back to richcompare.
  Soft `mveq` cdef-only; on `cypy` / `cypy.hot` / `cypy.buffers`.

## [1.4.0] — 2026-07-22 — `array_eq`

### Added

- **`array_eq`** (`cyarray`): typed `array.array` equality — identity/typecode/len
  short-circuit + `memcmp` over `itemsize * len` (mirrors `bytes_eq`). Soft
  letter `ayeq` stays cdef-only; preferred name on `cypy` / `cypy.hot` /
  `cypy.buffers`. Different typecodes compare false (same as Python `==`).

## [1.3.0] — 2026-07-22 — `bytearray_eq`

### Added

- **`bytearray_eq`** (`cybytearray`): typed `bytearray` equality — identity/len
  short-circuit + `memcmp` on `PyByteArray_AS_STRING` (mirrors `bytes_eq`). Soft
  letter `baeq` stays cdef-only; preferred name on `cypy` / `cypy.hot` /
  `cypy.buffers`.

## [1.2.0] — 2026-07-22 — `unicode_from_string`

### Added

- **`unicode_from_string`** (`cyunicode`): cimport thin wrapper for
  `PyUnicode_FromString` (no intern). Sibling of `uintern_from_string`;
  mirrors `bytes_from_string`.

## [1.1.0] — 2026-07-22 — `bytes_eq`

### Added

- **`bytes_eq`** (`cybytes`): typed `bytes` equality — identity/len short-circuit +
  `memcmp` on `PyBytes_AS_STRING` (mirrors `str_eq`). Soft letter `beq` stays
  cdef-only; preferred name on `cypy` / `cypy.hot` / `cypy.buffers`.

## [1.0.0] — 2026-07-21 — Core freeze

### Frozen

- **Core** public set: [`cypy.__all__`](src/cypy/__init__.py) + [`cypy.hot`](src/cypy/hot.py)
  — additive minors OK; removals / semantic changes need a major (see
  [`docs/RELEASE.md`](docs/RELEASE.md)).
- **Cimport contracts** for Core + documented `cdef` helpers: see
  [`COVERAGE.md`](COVERAGE.md) § “1.0 freeze” and per-module Surface / inventory
  in [`docs/modules/`](docs/modules/).

### Post-1.0 policy (Protocols / Runtime)

These tiers are **not** part of the Core freeze. They may still evolve under
**minors** after 1.0 (additions preferred; removals need deprecation + major
when they were public):

| Tier | Examples | Guidance |
|------|----------|----------|
| **Protocols** | `map_*`, `seq_*`, `num_*`, most `obj_*` | Prefer typed Core when the concrete type is known; `cypy.protocols` is provisional |
| **Runtime** | `dt_*`, `codec_*`, `time_*`, marshal/file/weakref/capsule/contextvars | Not micro-opt defaults; embedding / higher-level bridges |
| **cimport-only** | `cyerr`, `cymem`, `cythread`, `cyatomic`, … | Cython SDK only — never pure-Python |

### DEMOTE_ROOT at 1.0

Soft-alias demotions completed in **0.3**. Protocol/Runtime families remain
importable but **outside** Core `__all__` / `cypy.hot` (no surprise barrel trim).

## [0.3.0] — hard trim (Strategy B)

### Breaking

Soft root aliases in [`cypy.compat.COMPAT_MAP`](src/cypy/compat.py) are **removed**
from the `cypy` barrel and from public `.pyi` stubs. Soft letter/bare/`*_string` /
`dt_delta_*` / `method_function` / `method_self` / `time_time` names are Cython
`cdef`-only where they remain as implementation. Prefer word-prefix / `str_*` /
`ansi_*` / `*_cstr` / `dt_timedelta_*` / `method_get_*` / `time_wall`.

`cypy.__getattr__` raises `AttributeError` with `soft_alias_removal_hint` for
removed soft names.

### Kept

**Semantic twins** (`dict_len`/`dict_size`, `list_len`/`list_size`, …) stay dual —
never identity-aliased.

## [0.2.0] — soft-alias window (Strategy B)

### Soft aliases (removed in 0.3)

Word-prefix / `str_*` / `ansi_*` / `*_cstr` / `dt_timedelta_*` / `method_get_*` /
`time_wall` preferred; letter/bare/`*_string`/… dual-exported for the soft window.

### Conventions & discovery (Wave 5)

- N3/N4 rules: [`docs/NAMING.md`](docs/NAMING.md)
- Overlap playbooks: `examples/py_overlap_*.py`
- Facades: `cypy.containers`, `cypy.buffers`, `cypy.protocols` (prefer `cypy.hot`)
- Export CI: `scripts/check_exports.py`

## [0.1.1] — prior

Phase 5/6 surface + skill + examples on git tags. See git history / GitHub releases.
