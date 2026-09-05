# cycellobject

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.cellobject` |
| Sources | `src/cypy/cycellobject.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Closure cell objects for Cython/function tooling.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| cell_check / new / get / set | public | |
| cell_eq / celleq | public | content eq (`cell_richcompare`); soft `celleq`; not `hot` |
| cell_get_unchecked / set_unchecked | cimport | GET/SET macros |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| cell_check / get / new | APPROVED | see benches |
| cell_set | APPROVED (API) | mutation |
| cell_eq / celleq | APPROVED | content equality (issue #37); not `hot` |
| GET/SET unchecked | APPROVED (cimport) | no checks / SET skips INCREF |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
P26-07-22 — `*_eq` inventory Tier A (`cyeq_inventory_bench`)|
| Next action | — |

## Decision log

| Function | Decision | Iteration |
|----------|----------|-----------|
| public | APPROVED | 1 |
| cell_eq / celleq | APPROVED | 1 |
| macros | APPROVED (cimport) | 1 |

## Bench notes

- Harness: [`bench/cycellobject_bench.py`](../../bench/cycellobject_bench.py)

## Bench results

Harness: [`bench/cycellobject_bench.py`](../../bench/cycellobject_bench.py) · tier A · CPython 3.14 · N=80_000

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| cell_check | cell | **0.48x** | APPROVED |
| cell_check | miss | **0.40x** | APPROVED |
| cell_get | filled | **0.51x** | APPROVED |
| cell_new | empty | **0.94x** | APPROVED (API) |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cycellobject.py`](../../bench/tier_b/cycellobject.py) · `cycellobject_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| cell_check | cell | 2.90±0.13ms | 3.04ms | 27.59±0.14ms | **0.11x** | 0.11x | cypy faster |

**Tier B takeaway:** primary `cell_check` **0.11x** vs typed Cython baseline (cell).



### `*_eq` inventory (Tier A depth)

Harness: [`bench/cyeq_inventory_bench.py`](../../bench/cyeq_inventory_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| cell_eq | identity | 0.95±0.04ms | 1.00ms | **0.51x** | 0.50x | APPROVED |
| cell_eq | same value | 1.36±0.06ms | 1.46ms | **0.72x** | 0.72x | APPROVED |
| cell_eq | ne | 1.34±0.02ms | 1.37ms | **0.71x** | 0.68x | APPROVED |
### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| cell_eq | identity | 2.52±0.01ms | 2.53ms | 11.53±0.04ms | **0.22x** | 0.22x | cypy faster |
| cell_eq | same value | 10.20±0.18ms | 10.34ms | 11.15±0.02ms | **0.91x** | 0.92x | cypy faster |
| cell_eq | ne | 10.05±0.06ms | 10.14ms | 11.51±0.02ms | **0.87x** | 0.88x | cypy faster |

**Tier B `*_eq` notes:**
- **`cell_eq`:** Identity **0.22x**; same-value/ne **0.87–0.91x** — identity short-circuit + richcompare.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. Identity **0.22x**; same-value/ne **0.87–0.91x** — identity short-circuit + richcompare.

**Tier B:** `cell_check` **0.10x** vs type-name baseline.

| Topic | Finding |
|-------|---------|
| Why check/get win | Slot check and `PyCell_Get` beat `CellType`/`cell_contents` attribute paths |
| Ownership / refcount | Public `cell_set` adjusts refs; `PyCell_SET` skips INCREF — cimport only |
| ABI / safety | Unchecked GET/SET macros assume a live cell; wrong type → undefined |
| Scale | Cell ops are O(1); no size crossover — cost is wrapper vs attribute |
| New(None) | Empty cell allowed; construction ~ties Python `types.CellType` |
| `cell_eq` | Content equality via richcompare (not identity); empty↔empty True; soft `celleq`; measured; leave off `hot` (clarity / not a starter) |

## Done when

- [x] Try-all + depth + benches + `.pyi`
