# cyref

| Field | Value |
|-------|--------|
| Status | present (cimport) |
| Maps to | `cpython.ref` |
| Sources | `src/cypy/cyref.pxd` |
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
| ref_is_uniquely_referenced / immortal / deferred / try_incref | cimport | 3.14 unstable |
| Py_CLEAR | — | REJECTED as wrapper (needs lvalue macro); cimport `cpython.ref.Py_CLEAR` |
| public surface | — | REJECTED |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| incref/decref/refcnt/unstable* | APPROVED (cimport) | compile smoke; ownership-critical |
| CLEAR wrapper | REJECTED | macro needs assignable lvalue |
| public cpdef | REJECTED | can free live objects / imbalance |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-07-21 — Phase 4 Tier B n/a |
| Next action | — |

## Decision log

| Function | Probe | Decision | Iteration |
|----------|-------|----------|-----------|
| INCREF/DECREF | macros; compile via cimport | APPROVED (cimport) | 1 |
| Unstable unique/immortal | ABI present 3.14 | APPROVED (cimport) | 1 |
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

## Done when

- [x] Inventory + try-all evidence + cimport exports + QUEUE
