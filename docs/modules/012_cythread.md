# cythread

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.pythread` + `PyEval_SaveThread` / `RestoreThread` |
| Sources | `src/picop/cythread.pxd`, `src/picop/cythread.pyx`, `src/picop/cythread_shim.h` |
| Surface | public (`guards_supported` / `interpreter_guard`) + cimport helpers |
| Tracker lifecycle | decided (lock/GIL slice try-all) |
| Format | v2 |
| Indexed | full (declared slice) |

## Why

Nogil lock acquire/release + GIL save/restore for extension hot paths.

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| WAIT_LOCK / NOWAIT_LOCK / PY_LOCK_* | cypy | cdef | cimport | re-exports |
| PyThread_type_lock | cypy | cdef | cimport | lock typedef |
| thread_allocate_lock / thread_free_lock | cypy | cdef | cimport | allocate/free siblings |
| thread_acquire / thread_release | cypy | cdef | cimport | nogil |
| thread_get_ident | cypy | cdef | cimport | `PyThread_get_thread_ident` (GIL; not nogil) |
| eval_save_thread / eval_restore_thread | cypy | cdef | cimport | GIL release/reacquire |
| TSS / start_new_thread / stacksize | C-API | tried | — | deferred / out of slice |
| PyInterpreterGuard / PyInterpreterView / PyThreadStateToken | C-API | new (3.15) | — | PEP 788; opaque, `void*` handles via shim |
| guards_supported / interpreter_guard | cypy | cpdef | public | guard context manager (3.15+); raises on 3.14 |
| guard_from_current / guard_from_view / guard_close | cypy | cdef | cimport | raw guard handles |
| view_from_current / view_from_main / view_close | cypy | cdef | cimport | interpreter views |
| threadstate_ensure / threadstate_ensure_from_view / threadstate_release | cypy | cdef | cimport | thread-state attach; GILState fallback pre-3.15 |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| lock + eval helpers | APPROVED (cimport) | nogil / pointer APIs |
| guards_supported / interpreter_guard | APPROVED (public) | hang-safe guard CM; Tier A probe pass |
| guard / view / threadstate helpers | APPROVED (cimport) | lifecycle API; Tier B informational (not a fast path) |
| TSS / start_new_thread | REJECTED (scope) | not this slice |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 3 |
| Last pass | 2026-11-13 — Order 077 interpreter guards (Tier A + Tier B, 3.14 & 3.15) |
| Next action | — |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| thread_* / eval_* | Need cdef mirrors | n/a | ABI present | APPROVED (cimport) | 1 |
| thread_get_ident | nogil wrapper | cythonize | GIL-marked API — drop nogil | APPROVED (cimport) | 2 |
| interpreter_guard | Safe public CM over PEP 788 guards | tier A probe 0.32x/0.37x | APPROVED (public) | 3 |
| guard pair vs GILState pair | Guard cheaper than GILState? | tier B: 6.40x slower (3.15) | lifecycle tool only — **not** a micro-opt | 3 |

## Bench notes

- Tier A: `bench/cythread_bench.py` (guard probe + CM overhead). Tier B: `bench/tier_b/cythread.py` (`cythread_tb.pyx`).

## Bench results

Harness: [`bench/cythread_bench.py`](../../bench/cythread_bench.py) · tier A · CPython 3.14.7 & 3.15.0rc2 · `N=80_000` × `runs=5` · warmup 0  
Gate: mean ratio ≤ 0.95 · **Primary:** `guards_supported` vs version check → **0.32x** · Summary: gate rows 1/1 pass per version

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| guards_supported | vs version check (3.14) | 2.16±0.06ms | 2.26ms | **0.32x** | 0.29x | APPROVED |
| guards_supported | vs version check (3.15) | 1.93±0.06ms | 2.03ms | **0.37x** | 0.35x | APPROVED |

Informational (no baseline can beat doing nothing):

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| interpreter_guard | acquire+close vs no-op (3.15) | 12.99±0.18ms | 13.14ms | 4.18x | 4.16x | overhead, informational |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cythread.py`](../../bench/tier_b/cythread.py) · `cythread_tb.pyx` · CPython 3.15.0rc2 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5` (3.14: n/a — fallback is the GILState pair itself)  
Ratio = cypy guard loop / raw `PyGILState_Ensure/Release` loop. **Informational** — guards are a lifecycle API, not a hot path.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| guard_from_current/guard_close | per iteration | 64.48±1.26ms | 66.52ms | 10.08±0.66ms | **6.40x** | 5.95x | baseline faster |
| threadstate_ensure/release | guard held | 85.68±4.55ms | 92.28ms | 9.97±0.77ms | **8.59x** | 8.19x | baseline faster |

**Tier B takeaway:** guard acquire costs a `PyMem_RawMalloc` + atomic CAS (~6x a cached GILState check); use guards for finalization safety, not for hot loops.

## Experiment conclusions

**Tier B:** n/a on 3.14 (fallback equals the GILState pair); measured on 3.15 — see Tier B table.

- **PEP 788 guards (Order 077):** `PyInterpreterGuard_FromCurrent` = `PyMem_RawMalloc` + atomic CAS on `interp->finalization_guards`; the interpreter cannot finalize while a guard is open. Forgetting `Close` hangs finalization forever, so `InterpreterGuard.__dealloc__` closes an unclosed guard. `PyThreadState_Ensure`/`Release` must be paired on the same thread — over-release is `Py_FatalError`, not an exception. Tokens are `typedef void` sentinels (sometimes the internal `NO_TSTATE_SENTINEL`, never a usable `PyThreadState*`): opaque, never dereference. Views store only the interpreter id; `FromMain` hard-codes id 0 and is wrong under subinterpreters — prefer `FromCurrent`. On <3.15 `guards_supported()` is False, `interpreter_guard()` raises `RuntimeError`, and `threadstate_ensure/release` fall back to `PyGILState_Ensure/Release`.
- **GIL:** `eval_save_thread` releases GIL; pair with `eval_restore_thread` on the same `PyThreadState*`. Free-threaded builds still use these for compatibility paths — verify against target runtime.
- **Locks:** `thread_acquire(..., NOWAIT_LOCK)` can return `PY_LOCK_FAILURE` / `PY_LOCK_INTR`; check status.
- **Aliases:** `thread_allocate_lock` / `thread_free_lock` / `thread_get_ident` wrapped (were imported but unused).

## Done when

- [x] Declared-slice inventory + aliases
- [x] Experiment conclusions
- [x] QUEUE updated
- [x] Order 077: PEP 788 guard/view/thread-state wrappers, 3.15+ guard CM, GILState fallback, Tier A/B evidence on 3.14 & 3.15
