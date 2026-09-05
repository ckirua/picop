# cyrange

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `range` (custom; thin public wrap) |
| Sources | `src/cypy/cyrange.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full (declared surface) |

## Why

Value equality for `range` (same sequence, not identity) in config/index call sites. Richcompare matches Python `range.__eq__` (empty, step sign, equivalent spans).

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| rqeq / range_eq | cypy | cpdef | public | identity + richcompare; soft `rqeq` |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| rqeq / range_eq | APPROVED | Tier A **0.59–0.84x** across shapes (issue #42); not `hot` |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 2 |
| Last pass | 2026-07-22 — Tier B `*_eq` inventory|
| Next action | — |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| range_eq | Beat Python `==` call overhead | Tier A shapes | **0.59–0.84x**, 8/8 gate | APPROVED (not hot) | 2 |

## Bench notes

- Harness: [`bench/cyrange_bench.py`](../../bench/cyrange_bench.py)

## Bench results

Harness: [`bench/cyrange_bench.py`](../../bench/cyrange_bench.py) · tier A · CPython 3.14 · N=80_000 × runs=11

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| range_eq | eq span | 1.55±0.09ms | 1.78ms | **0.74x** | 0.79x | APPROVED |
| range_eq | ne span | 1.37±0.12ms | 1.65ms | **0.75x** | 0.85x | APPROVED |
| range_eq | identity | 0.98±0.11ms | 1.26ms | **0.59x** | 0.69x | APPROVED |
| range_eq | eq empty | 1.28±0.10ms | 1.54ms | **0.72x** | 0.84x | APPROVED |
| range_eq | eq equiv step | 1.61±0.18ms | 2.05ms | **0.69x** | 0.78x | APPROVED |
| range_eq | ne step | 1.36±0.12ms | 1.66ms | **0.75x** | 0.88x | APPROVED |
| range_eq | eq large | 1.80±0.06ms | 1.95ms | **0.84x** | 0.85x | APPROVED |
| range_eq | eq reversed | 1.60±0.08ms | 1.73ms | **0.77x** | 0.76x | APPROVED |

Summary: 8/8 faster · 8/8 ≥5% gate · mean **0.73x** · median **0.74x**.

### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| range_eq | eq | 15.98±0.06ms | 16.06ms | 15.33±0.11ms | **1.04x** | 1.04x | baseline faster |
| range_eq | ne | 9.49±0.05ms | 9.56ms | 9.35±0.05ms | **1.01x** | 1.01x | ~tie |
| range_eq | equiv span | 15.95±0.05ms | 16.03ms | 15.29±0.04ms | **1.04x** | 1.04x | baseline faster |

**Tier B `*_eq` notes:**
- **`range_eq`:** ~tie / slight lose (**1.01–1.04x**) vs Cython `range == range`; Tier A still wins vs Python.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. ~tie / slight lose (**1.01–1.04x**) vs Cython `range == range`; Tier A still wins vs Python.

| Topic | Finding |
|-------|---------|
| Why win | CPython `range_eq` is already O(1) (len + start/step); Tier A win is mostly avoiding Python `==` call / method overhead |
| Scale | Large ranges still **0.84x** — cost stays O(1); no element walk |
| Semantics | Same as `range.__eq__` (empty equal; equiv spans with different stop; step signs). Soft `rqeq` COMPAT-only |
| Ownership | No borrowed pointers — safe |

## Done when

- [x] Declared surface inventory
- [x] Workflow + decision log
- [x] Tier A harness + tracker tables (no smoke placeholders)
- [x] Smoke example + exports + CHANGELOG
