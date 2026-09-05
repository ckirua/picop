# cypycapsule

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.pycapsule` |
| Sources | `src/cypy/cypycapsule.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

Capsule type checks public; pointer get/set cimport (void*).

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| capsule_check_exact / is_valid | public | |
| capsule_eq / capsuleeq | public | identity eq (`object.__eq__`); soft `capsuleeq`; not `hot` |
| new / get_pointer / set_* / import | cimport | void* |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| check_exact / is_valid | APPROVED | see benches |
| capsule_eq / capsuleeq | APPROVED | identity equality (issue #38); not `hot` |
| pointer APIs | APPROVED (cimport) | void* |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-07-22 — Tier B `*_eq` inventory|
| Next action | — |

## Decision log

| Function | Decision | Iteration |
|----------|----------|-----------|
| public | APPROVED | 1 |
| capsule_eq / capsuleeq | APPROVED | 1 |
| pointer APIs | APPROVED (cimport) | 1 |

## Bench notes

- Harness: [`bench/cypycapsule_bench.py`](../../bench/cypycapsule_bench.py)

## Bench results

Harness: [`bench/cypycapsule_bench.py`](../../bench/cypycapsule_bench.py) · tier A · CPython 3.14 · N=80_000

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| capsule_check_exact | capsule | **0.31x** | APPROVED |
| capsule_is_valid | name match | **0.31x** | APPROVED |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cypycapsule.py`](../../bench/tier_b/cypycapsule.py) · `cypycapsule_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| capsule_check_exact | capsule | 2.89±0.24ms | 3.17ms | 28.42±0.26ms | **0.10x** | 0.11x | cypy faster |

**Tier B takeaway:** primary `capsule_check_exact` **0.10x** vs typed Cython baseline (capsule).



### `capsule_eq` (Tier A depth)

Harness: [`bench/cyeq_misc_bench.py`](../../bench/cyeq_misc_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| capsule_eq | identity | 0.98±0.05ms | 1.09ms | **0.55x** | 0.59x | APPROVED |
| capsule_eq | ne | 1.00±0.03ms | 1.07ms | **0.55x** | 0.57x | APPROVED |

### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| capsule_eq | identity | 2.49±0.01ms | 2.50ms | 4.99±0.02ms | **0.50x** | 0.50x | cypy faster |
| capsule_eq | ne | 2.50±0.00ms | 2.50ms | 6.18±0.03ms | **0.41x** | 0.40x | cypy faster |

**Tier B `*_eq` notes:**
- **`capsule_eq`:** **0.41–0.50x** win — identity.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. **0.41–0.50x** win — identity.

**Tier B:** `capsule_check_exact` **0.10x** vs type-name baseline.

| Topic | Finding |
|-------|---------|
| Why checks win | Exact type + name validation in C beats Python capsule introspection |
| Ownership / safety | `GetPointer` returns `void*` — never public; destructor is C fn or NULL |
| ABI | Pointer get/set/import stay cimport; wrong name → NULL / exception |
| Scale | Check is O(1); no payload size — capsule holds an opaque pointer |
| Prefer | Public checks for gates; all pointer mutation in cdef under GIL |
| `capsule_eq` | Identity only (`a is b`); same pointer/name ≠ equal; soft `capsuleeq`; measured; leave off `hot` (clarity / not a starter) |

## Done when

- [x] Try-all + depth + benches + `.pyi`
