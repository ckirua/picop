# cyversion

| Field | Value |
|-------|--------|
| Status | present (cimport) |
| Maps to | `cpython.version` |
| Sources | `src/cypy/cyversion.pxd` |
| Surface | cimport only |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

Re-export ``PY_VERSION_HEX`` and friends for Cython ``if`` at C compile time.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| PY_VERSION_HEX / MAJOR / MINOR / MICRO / RELEASE_* / PY_VERSION | cimport | |
| public | — | REJECTED (use ``sys.version_info``) |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| version constants | APPROVED (cimport) | compile-time |
| public | REJECTED | runtime already has sys |

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
| Why cimport | `PY_VERSION_HEX` and friends are compile-time constants — use in Cython `if`, not runtime benches |
| ABI | MAJOR/MINOR/MICRO/RELEASE_*/PY_VERSION re-exported for feature gates |
| Safety | Prefer `if PY_VERSION_HEX >= 0x030e0000:` over fragile IF/DEF sprawl |
| GIL | N/A — no runtime API; public REJECTED in favor of `sys.version_info` |
| Prefer | cimport for C compile gates; Python introspection stays on `sys` |

## Done when

- [x] Try-all evidence + cimport + QUEUE
