# cyinstance

| Field | Value |
|-------|--------|
| Status | absent (ABI gone) |
| Maps to | `cpython.instance` |
| Sources | — |
| Surface | none |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

Classic-class instance API from Python 2. Entire surface missing on CPython 3.14.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| PyInstance_Check | — | REJECTED |
| PyInstance_New | — | REJECTED |
| PyInstance_NewRaw | — | REJECTED |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| all | REJECTED | ctypes AttributeError on libpython3.14; classic classes removed |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-07-21 — Phase 4 Tier B n/a |
| Next action | — |

## Decision log

| Function | Probe | Decision | Iteration |
|----------|-------|----------|-----------|
| PyInstance_* | ctypes missing | REJECTED | 1 |

## Bench notes

- n/a (no symbols)

## Bench results

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| — | ABI missing | — | n/a |

### Tier B (Cython baseline)

| operation | case | cypy mean±σ | p99 | ratio | note |
|-----------|------|-------------|-----|-------|------|
| — | — | — | — | n/a | Surface **none** (REJECTED ABI) — no helpers to microbench |

**Tier B takeaway:** n/a — module has no shippable API surface.

## Experiment conclusions

**Tier B:** n/a (surface none).

| Topic | Finding |
|-------|---------|
| ABI | No `PyInstance_*` in 3.14 headers/lib — classic class model removed in Python 3 |
| Wrapper | No cimport surface worth keeping; Cython Includes are historical |
| ABI | No `PyInstance_*` exports on 3.14 — classic classes removed in Python 3 |
| Why REJECTED | Headers/Includes are historical; wrapping would be dead code |
| Safety | N/A — no runtime surface |
| Demotion | Document only; do not ship helpers |


## Done when

- [x] Try-all evidence + REJECTED with why + QUEUE
