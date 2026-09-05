# cymem

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.mem` |
| Sources | `src/cypy/cymem.pxd` |
| Surface | cimport only |
| Tracker lifecycle | decided (try-all + cheap aliases) |
| Format | v2 |
| Indexed | full |

## Why

Python-heap / pymalloc / raw allocators for extension arenas.

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| mem_malloc / mem_calloc / mem_realloc / mem_free | cypy | cdef | cimport | `PyMem_*` |
| mem_raw_malloc / mem_raw_realloc / mem_raw_free | cypy | cdef | cimport | `PyMem_Raw*` nogil |
| obj_malloc / obj_calloc / obj_realloc / obj_free | cypy | cdef | cimport | `PyObject_*` |
| PyMem_Del / deprecated macros | C-API | tried | — | REJECTED alias of free |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| all wrapped allocators | APPROVED (cimport) | pointers — not public Python |
| PyMem_Del | REJECTED | legacy free alias |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-07-21 — Phase 4 Tier B n/a |
| Next action | — |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| mem_*/obj_* | Need cdef mirrors | n/a | ABI present | APPROVED (cimport) | 1 |

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

- **Why cimport:** returns `void*` — useless/unsafe as public Python API.
- **Raw vs PyMem:** `mem_raw_*` is nogil-safe; `mem_*` may need GIL depending on allocator hooks.
- **Free-threaded:** same allocator rules as CPython extensions; pair malloc/free families correctly (never free Raw with PyMem_Free).
- **Aliases:** Calloc + Raw* + Obj Realloc/Calloc added per cheap-sibling rule.

## Done when

- [x] Full `cpython.mem` wrap of public allocators
- [x] Experiment conclusions
- [x] QUEUE updated
