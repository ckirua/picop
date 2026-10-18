# cyerr

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.exc` (thin slice) |
| Sources | `src/picop/cyerr.pxd` |
| Surface | cimport only |
| Tracker lifecycle | decided — raised-exception lifecycle added |
| Format | v2 |
| Indexed | full (declared slice) |

## Why

GIL-held error-indicator helpers for nogil→gil boundaries in extensions.

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| err_clear | cypy | cdef | cimport | `PyErr_Clear` |
| err_occurred | cypy | cdef | cimport | `PyErr_Occurred() != NULL` |
| err_exception_matches | cypy | cdef | cimport | `PyErr_ExceptionMatches` — UB if no error |
| err_set_string | cypy | cdef | cimport | `PyErr_SetString` |
| err_set_object | cypy | cdef | cimport | `PyErr_SetObject` sibling |
| err_set_none | cypy | cdef | cimport | `PyErr_SetNone` sibling |
| err_no_memory | cypy | cdef | cimport | `PyErr_NoMemory` |
| err_fetch / err_restore | cypy | cdef | cimport | legacy triple; deprecated by CPython since 3.12 |
| err_get_raised / err_set_raised | picop | cdef | cimport | preferred Python ≥3.14 lifecycle; new-ref get / stealing set |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| err_* (all wrapped) | APPROVED (cimport) | unsafe/pointless from Python; GIL required |
| Format/Warn/Print/… | REJECTED (scope) | not current slice |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-07-21 — Phase 4 Tier B n/a |
| Next action | — |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| err_* | Need cdef mirrors | n/a (cimport) | compiles / used pattern | APPROVED (cimport) | 1 |

## Bench notes

- Harness: n/a (cimport-only — no public `cpdef`)
- Env: CPython 3.14.6 · Linux x86_64 · GIL required for all `PyErr_*`

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

- **Why cimport:** error indicator is thread-local under GIL; Python already has exceptions — wrappers are for C-level paths after `nogil`.
- **Safety:** `err_exception_matches` is UB if no error set; `err_fetch`/`err_restore` steal references.
- **Free-threaded:** still per-thread error state; always hold GIL around these calls.
- **Aliases added:** `err_set_object`, `err_set_none`, `err_exception_matches`, `err_fetch`, `err_restore`.

## Done when

- [x] Declared-slice inventory + aliases
- [x] Experiment conclusions (no public bench)
- [x] QUEUE + exports updated
