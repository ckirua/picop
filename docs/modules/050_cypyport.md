# cypyport

| Field | Value |
|-------|--------|
| Status | present (cimport) |
| Maps to | `cpython.pyport` |
| Sources | `src/cypy/cypyport.pxd` |
| Surface | cimport only |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

Re-export ssize limits and fixed-width typedefs for Cython callers.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| PY_SSIZE_T_MIN / MAX | cimport | |
| int32_t / int64_t / uint32_t / uint64_t | cimport | |
| public | — | REJECTED |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| typedefs / limits | APPROVED (cimport) | compile-time constants/types |
| public cpdef | REJECTED | no runtime helpers |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-07-21 — Phase 4 Tier B n/a |
| Next action | — |

## Bench notes

- n/a

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
| Why cimport | ssize limits and fixed-width typedefs are compile-time — nothing to bench from Python |
| ABI | `PY_SSIZE_T_MIN/MAX` and `int32_t`/`int64_t`/`uint*` re-exported for consistent cypy surface |
| Safety | Using wrong width at C boundaries is a classic overflow bug; prefer these typedefs over ad-hoc `long` |
| GIL | N/A — no runtime calls; pure types/constants |
| Prefer | `cimport cypy.cypyport` over raw Cython Includes for one package-shaped portability header |

## Done when

- [x] Try-all evidence + cimport + QUEUE
