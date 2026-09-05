# cythread

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.pythread` + `PyEval_SaveThread` / `RestoreThread` |
| Sources | `src/cypy/cythread.pxd` |
| Surface | cimport only |
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

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| lock + eval helpers | APPROVED (cimport) | nogil / pointer APIs |
| TSS / start_new_thread | REJECTED (scope) | not this slice |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 2 |
| Last pass | 2026-07-22 — `thread_get_ident` drop nogil (barrel cimport) |
| Next action | — |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| thread_* / eval_* | Need cdef mirrors | n/a | ABI present | APPROVED (cimport) | 1 |
| thread_get_ident | nogil wrapper | cythonize | GIL-marked API — drop nogil | APPROVED (cimport) | 2 |

## Bench notes

- n/a (cimport-only)

## Bench results

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| — | cimport-only | — | — | — | — | n/a |

### Tier B (Cython baseline)

| operation | case | cypy mean±σ | p99 | ratio | note |
|-----------|------|-------------|-----|-------|------|
| — | — | — | — | n/a (cimport) | No public `cpdef` hot path — cimport-only surface; Tier B harness not applicable |

**Tier B takeaway:** n/a (cimport) — no public helper to compare against a typed Cython baseline.

## Experiment conclusions

**Tier B:** n/a (cimport).

- **GIL:** `eval_save_thread` releases GIL; pair with `eval_restore_thread` on the same `PyThreadState*`. Free-threaded builds still use these for compatibility paths — verify against target runtime.
- **Locks:** `thread_acquire(..., NOWAIT_LOCK)` can return `PY_LOCK_FAILURE` / `PY_LOCK_INTR`; check status.
- **Aliases:** `thread_allocate_lock` / `thread_free_lock` / `thread_get_ident` wrapped (were imported but unused).

## Done when

- [x] Declared-slice inventory + aliases
- [x] Experiment conclusions
- [x] QUEUE updated
