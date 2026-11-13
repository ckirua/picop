# cyref

| Field | Value |
|-------|--------|
| Status | present (cimport) |
| Maps to | `cpython.ref` |
| Sources | `src/picop/cyref.pxd` |
| Surface | cimport only |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

Refcount macros and 3.14 unstable unique-ref helpers for Cython. Not safe as a public Python API.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| ref_incref / xincref / decref / xdecref | cimport | |
| ref_refcnt | cimport | immortal caveat |
| ref_set_immortal | cimport | 3.15 `PyUnstable_SetImmortal`; refcount-pin emulation on 3.14 GIL builds, refused on 3.14 free-threaded (Order 078) |
| Py_CLEAR | — | REJECTED as wrapper (needs lvalue macro); cimport `cpython.ref.Py_CLEAR` |
| public surface | — | REJECTED |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| ref_set_immortal | APPROVED (cimport) | uniform API via cyref_shim.h |
| CLEAR wrapper | REJECTED | macro needs assignable lvalue |
| public cpdef | REJECTED | can free live objects / imbalance |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 2 |
| Last pass | 2026-11-13 — Order 078 ref_set_immortal (smoke demo, 3.14 & 3.15) |
| Next action | — |

## Decision log

| Function | Probe | Decision | Iteration |
|----------|-------|----------|-----------|
| INCREF/DECREF | macros; compile via cimport | APPROVED (cimport) | 1 |
| ref_set_immortal | Uniform immortal-pinning helper | smoke: pins unique-ref list, refuses shared ref | APPROVED (cimport) | 2 |
| CLEAR wrap | cannot clear caller ptr safely | REJECTED | 1 |
| public | ownership hazard | REJECTED | 1 |

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
| Ownership | DECREF may run `__del__` with globals mutable — Cython only |
| Immortal | `Py_REFCNT` not precise for immortal objects |
| Unique-ref | Prefer `ref_is_uniquely_referenced` over `refcnt==1` (free-threaded) |
| CLEAR | Use `Py_CLEAR` from `cpython.ref` on a C variable, not a Python-visible wrapper |
- `ref_set_immortal` pins `ob_refcnt` at the immortal threshold — the object is never freed; returns 0 without pinning for non-unique refs or str, mirroring 3.15 `PyUnstable_SetImmortal`.

## Done when

- [x] Inventory + try-all evidence + cimport exports + QUEUE
- [x] `ref_set_immortal` documented and smoke-tested on 3.14 and 3.15
