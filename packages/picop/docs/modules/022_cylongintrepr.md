# cylongintrepr

| Field | Value |
|-------|--------|
| Status | present (cimport) |
| Maps to | `cpython.longintrepr` |
| Sources | `src/cypy/cylongintrepr.pxd` |
| Surface | cimport only |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

Digit-level `int` internals for advanced builders. Not safe as a public Python API.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| longrepr_new | cimport | `_PyLong_New` — uninit digits |
| longrepr_digits | cimport | `long_value.ob_digit` (3.14 layout) |
| digit / sdigit / py_long | cimport | re-export types |
| PyLong_SHIFT / BASE / MASK | cimport | re-export constants |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| longrepr_new / digits | APPROVED (cimport) | internals; uninit |
| types / SHIFT/BASE/MASK | APPROVED (cimport) | needed by callers |
| public surface | REJECTED | no safe Python API |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 2 |
| Last pass | 2026-07-22 — `longrepr_digits` via `long_value.ob_digit` (barrel cimport) |
| Next action | — |

## Decision log

| Function | Probe | Decision | Iteration |
|----------|-------|----------|-----------|
| _PyLong_New | ABI present; uninit digits | APPROVED (cimport) | 1 |
| public wrap | would leak uninit / layout | REJECTED | 1 |
| longrepr_digits | flat `ob_digit` vs 3.14 `long_value` | APPROVED — C helper for layout | 2 |

## Bench notes

- n/a (cimport-only; no public `cpdef`)

## Bench results

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| — | cimport-only | — | n/a |

### Tier B (Cython baseline)

| operation | case | cypy mean±σ | p99 | ratio | note |
|-----------|------|-------------|-----|-------|------|
| — | — | — | — | n/a (cimport) | No public `cpdef` hot path — cimport-only surface; Tier B harness not applicable |

**Tier B takeaway:** n/a (cimport) — no public helper to compare against a typed Cython baseline.

## Experiment conclusions

**Tier B:** n/a (cimport).

| Topic | Finding |
|-------|---------|
| Uninit | `_PyLong_New(n)` does not zero digits — must fill `ob_digit` before incref to Python |
| Layout | `PyLong_SHIFT`/`BASE`/`MASK` version-sensitive — cimport constants, don't hardcode |
| Public | No benchable public surface without exposing undefined memory |
| Why cimport | Digit/ob_size layout is internal; public int API is `cylong` |
| ABI | `_PyLong_New` / digit macros not a stable public accelerator surface |
| Safety | Mutating digit buffers without unique ownership is UB |
| Demotion | Keep cdef helpers for Cython extensions that already touch longobject.h |


## Done when

- [x] Inventory + try-all evidence + cimport exports + QUEUE
