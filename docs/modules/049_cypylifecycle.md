# cypylifecycle

| Field | Value |
|-------|--------|
| Status | present (cimport) |
| Maps to | `cpython.pylifecycle` |
| Sources | `src/cypy/cypylifecycle.pxd` |
| Surface | cimport only |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

Initialize/Finalize and version string for embedding. Public REJECTED.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| life_initialize* / is_initialized / finalize* / get_version | cimport | |
| SetProgramName / GetPath family (wchar) | — | REJECTED as incomplete wrappers |
| public | — | REJECTED |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| Initialize / Finalize / IsInitialized / GetVersion | APPROVED (cimport) | ABI present |
| public | REJECTED | tears down whole process |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 2 |
| Last pass | 2026-07-22 — drop unused wchar externs (barrel cimport) |
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

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| life_* (Initialize/Finalize/GetVersion) | Need cdef mirrors | n/a | ABI present | APPROVED (cimport) | 1 |
| wchar Get/SetProgramName | Incomplete wrappers | cythonize | undeclared `wchar_t` broke barrel cimport — drop externs | REJECTED | 2 |

## Experiment conclusions

**Tier B:** n/a (cimport).

| Topic | Finding |
|-------|---------|
| Why cimport | Initialize/Finalize tear down or boot the whole interpreter — not a casual public helper |
| ABI | Initialize / IsInitialized / Finalize / GetVersion symbols present for embedding |
| Safety / GIL | Finalize destroys the interpreter under process-wide assumptions; never expose as `cpdef` |
| Ownership | GetVersion returns a static `const char*` — no free; wchar path helpers REJECTED as incomplete |
| Prefer | Embedding/Cython only; Python code uses `sys` / process lifecycle, not pylifecycle wrappers |

## Done when

- [x] Try-all evidence + cimport + QUEUE
