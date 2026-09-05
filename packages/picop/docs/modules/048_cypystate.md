# cypystate

| Field | Value |
|-------|--------|
| Status | present (cimport) |
| Maps to | `cpython.pystate` |
| Sources | `src/cypy/cypystate.pxd` |
| Surface | cimport only |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

GIL ensure/release and thread-state dict for Cython. Interpreter New/Delete/Swap rejected as too footgun-y.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| pystate_get / get_dict / gil_ensure / gil_release | cimport | |
| Interpreter New/Clear/Delete / ThreadState Swap | — | REJECTED |
| public | — | REJECTED |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| get / get_dict / gil_* | APPROVED (cimport) | ABI present |
| Swap / interpreter lifecycle | REJECTED | fatal misuse risk |
| public | REJECTED | process-only |

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
| Why cimport | GIL ensure/release and thread-state dict are process/thread footguns as public APIs |
| GIL | `gil_ensure`/`gil_release` must be paired; opaque handle — mismatch → deadlock or crash |
| Borrowed / ownership | `GetDict` returns borrowed; any wrapper must INCREF before exposing |
| ABI / safety | Interpreter New/Clear/Delete and ThreadState Swap REJECTED — Cython Includes warn DO NOT USE |
| Prefer | Keep ensure/release for cdef extension code; never Swap from cypy public surface |

## Done when

- [x] Try-all evidence + cimport + QUEUE
