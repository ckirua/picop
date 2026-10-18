# cygenobject

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.genobject` |
| Sources | `src/cypy/cygenobject.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Generator type checks. Construction steals frames — cimport only.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| gen_check / exact | public | |
| gen_eq / geneq | public | identity eq (`object.__eq__`); soft `geneq`; not `hot` |
| gen_new / new_with_qualname | cimport | steals frame |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| gen_check* | APPROVED | type-slot vs isinstance |
| gen_eq / geneq | APPROVED | identity equality (issue #40); not `hot` |
| gen_new* | APPROVED (cimport) | steals frame ref |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-07-22 — Tier B `*_eq` inventory|
| Next action | — |

## Decision log

| Function | Decision | Iteration |
|----------|----------|-----------|
| check* | APPROVED | 1 |
| gen_eq / geneq | APPROVED | 1 |
| new* | APPROVED (cimport) | 1 |

## Bench notes

- Harness: [`bench/cygenobject_bench.py`](../../bench/cygenobject_bench.py)

## Bench results

Harness: [`bench/cygenobject_bench.py`](../../bench/cygenobject_bench.py) · tier A · CPython 3.14 · N=80_000

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| gen_check | generator | **0.50x** | APPROVED |
| gen_check | list (miss) | **0.41x** | APPROVED |
| gen_check_exact | generator | **0.51x** | APPROVED |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cygenobject.py`](../../bench/tier_b/cygenobject.py) · `cygenobject_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| gen_check | gen | 2.84±0.11ms | 2.97ms | 6.63±0.06ms | **0.43x** | 0.44x | cypy faster |

**Tier B takeaway:** primary `gen_check` **0.43x** vs typed Cython baseline (gen).



### `gen_eq` (Tier A depth)

Harness: [`bench/cyeq_misc_bench.py`](../../bench/cyeq_misc_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| gen_eq | identity | 0.99±0.06ms | 1.12ms | **0.56x** | 0.62x | APPROVED |
| gen_eq | ne | 1.05±0.08ms | 1.17ms | **0.57x** | 0.61x | APPROVED |

### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| gen_eq | identity | 2.50±0.01ms | 2.50ms | 4.99±0.02ms | **0.50x** | 0.50x | cypy faster |
| gen_eq | ne | 2.50±0.00ms | 2.51ms | 6.17±0.02ms | **0.41x** | 0.40x | cypy faster |

**Tier B `*_eq` notes:**
- **`gen_eq`:** **0.41–0.50x** win — identity.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. **0.41–0.50x** win — identity.

**Tier B:** `gen_check` **0.43x** vs GeneratorType isinstance.

| Topic | Finding |
|-------|---------|
| Why checks win | Type-slot / exact-type tests beat `isinstance(GeneratorType)` MRO walk |
| Steal / ownership | `gen_new*` steals the `PyFrameObject*` — never expose as public `cpdef` |
| ABI / safety | Frame steal is a hard ABI contract; wrong ownership → crash / double-free |
| QualName | Cheap sibling of New; same steal semantics — cimport only |
| Prefer | Public checks for type gates; construction stays cdef for Cython runtime authors |
| `gen_eq` | Identity (`a is b`) — CPython `object.__eq__`; soft `geneq`; measured; leave off `hot` (clarity / not a starter) |

## Done when

- [x] Try-all + depth + benches + `.pyi`
