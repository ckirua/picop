# cyiterobject

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.iterobject` |
| Sources | `src/cypy/cyiterobject.pxd`, `.pyx`, `.pyi` |
| Surface | public |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Sequence and callable iterator constructors.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| seqiter_check / new | public | |
| calliter_check / new | public | |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| seqiter_check / calliter_check | APPROVED | type-slot checks |
| seqiter_new / calliter_new | APPROVED (API) | match builtins |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-07-21 — Phase 4 Tier B |
| Next action | — |

## Decision log

| Function | Decision | Iteration |
|----------|----------|-----------|
| all | APPROVED / API | 1 |

## Bench notes

- Harness: [`bench/cyiterobject_bench.py`](../../bench/cyiterobject_bench.py) · N=80000

## Bench results

Harness: [`bench/cyiterobject_bench.py`](../../bench/cyiterobject_bench.py) · tier A · CPython 3.14 · N=80_000

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| seqiter_check | seqiter | **0.31x** | APPROVED |
| seqiter_new | list | **1.37x** | APPROVED (API) |
| calliter_check | calliter | **0.33x** | APPROVED |
| calliter_new | callable | **1.04x** | APPROVED (API) |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cyiterobject.py`](../../bench/tier_b/cyiterobject.py) · `cyiterobject_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| seqiter_check | list_iter | 2.96±0.05ms | 3.01ms | 26.90±0.11ms | **0.11x** | 0.11x | cypy faster |

**Tier B takeaway:** primary `seqiter_check` **0.11x** vs typed Cython baseline (list_iter).


## Experiment conclusions

**Tier B:** `seqiter_check` **0.11x** vs type-name baseline.

| Topic | Finding |
|-------|---------|
| Why checks win | Slot/type-flag macros beat Python name/`isinstance` heuristics; no attribute walk |
| Why constructors lose | Same C `iter` path plus `cpdef` wrapper frame; builtins already specialized |
| Scale | Check cost is O(1) type test; construction dominated by iterator object alloc regardless of sequence length |
| ABI / safety | Check macros are compile-time (ctypes missing); New returns owned refs — no steal from the iterable |
| Prefer | Use checks in hot Cython filters; prefer builtin `iter` from Python when constructing |

## Done when

- [x] Try-all + depth + benches + `.pyi`

### Stub visibility (2026-08-02)

- Stub-hidden (Tier A `>1.02x`): `seqiter_new`, `calliter_new`. Still `cpdef`.

