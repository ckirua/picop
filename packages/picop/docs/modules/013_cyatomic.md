# cyatomic

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | custom (C11 `stdatomic` + `cyatomic_shim.h`) |
| Sources | `src/cypy/cyatomic.pxd`, `cyatomic_shim.h` |
| Surface | cimport only |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full (declared custom surface) |

## Why

Nogil SPSC / lock-free index helpers — not a CPython include twin.

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| memory_order_* | cypy | cdef | cimport | C11 enum constants |
| atomic_size_t / atomic_init | cypy | cdef | cimport | size_t atomics |
| atomic_load_{relaxed,acquire} | cypy | cdef | cimport | |
| atomic_store_{relaxed,release} | cypy | cdef | cimport | |
| atomic_fetch_add_relaxed / atomic_cas_weak_relaxed | cypy | cdef | cimport | |
| atomic_uint64_* | cypy | cdef | cimport | shim `_Atomic uint64_t` |
| CPython atomics | — | — | — | N/A |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| all helpers | APPROVED (cimport) | nogil pointers — not public Python |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-07-21 — Phase 4 Tier B n/a |
| Next action | — |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| atomic_* | SPSC helpers | n/a | compiles | APPROVED (cimport) | 1 |

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

- **Ordering:** typical SPSC uses store-release on producer tail + load-acquire on consumer head; relaxed for local capacity checks.
- **Free-threaded:** these are C11 atomics independent of the GIL — correct for rings shared across Python threads / nogil sections.
- **Shim:** `atomic_uint64_t` via `cyatomic_shim.h` because Cython lacks a portable `_Atomic uint64_t` typedef in-tree.
- **Exports:** previously missing `atomic_uint64_load_acquire` / `store_*` and `memory_order_acq_rel` / `seq_cst` now re-exported from `__init__.pxd`.

## Done when

- [x] Full custom inventory
- [x] Experiment conclusions
- [x] QUEUE updated
