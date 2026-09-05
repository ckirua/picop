# cyceval

| Field | Value |
|-------|--------|
| Status | present (cimport) |
| Maps to | `cpython.ceval` |
| Sources | `src/cypy/cyceval.pxd` |
| Surface | cimport only |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

Process-wide thread/GIL init probes. Not a public Python API.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| eval_init_threads / eval_threads_initialized | cimport | |
| public | — | REJECTED |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| InitThreads / ThreadsInitialized | APPROVED (cimport) | ABI present; process-only |
| public cpdef | REJECTED | process-wide side effects |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-07-21 — Phase 4 Tier B n/a |
| Next action | — |

## Bench notes

- n/a (cimport-only)

## Bench results

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| — | cimport-only | — | — | n/a | — | n/a (cimport) |

### Tier B (Cython baseline)

| operation | case | cypy mean±σ | p99 | ratio | note |
|-----------|------|-------------|-----|-------|------|
| — | — | — | — | n/a (cimport) | No public `cpdef` hot path — cimport-only surface; Tier B harness not applicable |

**Tier B takeaway:** n/a (cimport) — no public helper to compare against a typed Cython baseline.

## Experiment conclusions

**Tier B:** n/a (cimport).

| Topic | Finding |
|-------|---------|
| Why cimport | Process-wide thread/GIL init is not a public helper surface |
| GIL / ABI | `PyEval_InitThreads` / `ThreadsInitialized` present; post-3.x InitThreads is effectively a no-op after runtime start |
| Safety | Calling from Python would imply process-global side effects with no useful return — REJECTED public |
| Ownership | No object refs involved; state is interpreter-global |
| Prefer | cdef probes for embedding/Cython only; do not expose as `cpdef` |

## Done when

- [x] Try-all evidence + cimport + QUEUE
