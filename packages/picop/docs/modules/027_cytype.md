# cytype

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.type` |
| Sources | `src/cypy/cytype.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Type-object checks for Cython. Mutation/alloc helpers stay cimport.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| type_check / exact / is_subtype | public | |
| type_eq / typeeq | public | identity (`a is b`); soft `typeeq`; not `hot` |
| modified / has_feature / is_gc / generic_* / ready | cimport | type mutation / flags |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| type_check* | APPROVED | **0.38–0.52x** |
| type_is_subtype | APPROVED (API) | **1.04–1.05x** ~tie vs issubclass |
| type_eq / typeeq | APPROVED | identity (issue #36); not `hot` |
| modified / ready / generic / flags | APPROVED (cimport) | type builder surface |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
P26-07-22 — `*_eq` inventory Tier A (`cyeq_inventory_bench`)|
| Next action | — |

## Decision log

| Function | Result | Decision | Iteration |
|----------|--------|----------|-----------|
| type_check* | 0.38–0.52x | APPROVED | 1 |
| is_subtype | 1.04–1.05x | APPROVED (API) | 1 |
| type_eq / typeeq | identity (`a is b`); not metaclass `__eq__` | APPROVED | 1 |
| cdef helpers | type mutation | APPROVED (cimport) | 1 |

## Bench notes

- Harness: [`bench/cytype_bench.py`](../../bench/cytype_bench.py) · N=80000

## Bench results

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| type_check | int / 3 / Sub | 0.50x / 0.38x / 0.46x | pass |
| type_check_exact | int / type | 0.52x / 0.52x | pass |
| type_is_subtype | bool⊂int / int⊄bool | 1.05x / 1.04x | API |

Summary: 5/7 gate · mean **0.64x**.

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cytype.py`](../../bench/tier_b/cytype.py) · `cytype_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| type_check | hit | 2.49±0.03ms | 2.54ms | 2.47±0.02ms | **1.01x** | 1.02x | ~tie |

**Tier B takeaway:** primary `type_check` **1.01x** vs typed Cython baseline (hit).



### `*_eq` inventory (Tier A depth)

Harness: [`bench/cyeq_inventory_bench.py`](../../bench/cyeq_inventory_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| type_eq | identity | 0.90±0.03ms | 0.95ms | **0.57x** | 0.58x | APPROVED |
| type_eq | ne | 0.90±0.03ms | 0.93ms | **0.54x** | 0.53x | APPROVED |
### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| type_eq | identity | 2.45±0.01ms | 2.46ms | 5.77±0.03ms | **0.42x** | 0.42x | cypy faster |
| type_eq | ne | 2.44±0.01ms | 2.46ms | 6.15±0.02ms | **0.40x** | 0.40x | cypy faster |

**Tier B `*_eq` notes:**
- **`type_eq`:** **0.40–0.42x** win — pointer/identity compare vs Cython `==`.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. **0.40–0.42x** win — pointer/identity compare vs Cython `==`.

**Tier B:** `type_check` **0.99x** — ~parity.

| Topic | Finding |
|-------|---------|
| Check win | Type-flag vs isinstance(type) |
| IsSubtype ~tie | Same C path as issubclass for types |
| Ready/Modified | Must run after manual `tp_*` edits — unsafe from Python |
| HasFeature/IS_GC | Flag macros — cdef |
| Why win | TypeObject slot checks vs isinstance(type) |
| Scale | IsSubtype bool<int ~tie with Python issubclass (1.03x) — clarity keep |
| Safety | Ready/Modified are process-global type mutations — not for hot paths |
| ABI | Heap-type helpers remain; classic class APIs gone (see cyinstance) |
| GCC 14+ | `PyType_*` externs take `type` (not `object`) + cast at wrappers — avoids `PyObject*`/`PyTypeObject*` incompatible-pointer errors when compiling `cytype.pxd` |
| `type_eq` | Identity (`a is b`) — CPython type default; not metaclass `__eq__`; soft `typeeq` (`teq` is `tuple_eq`); measured; leave off `hot` (clarity / not a starter) |


## Done when

- [x] Try-all + depth + benches + `.pyi`

### Stub visibility (2026-08-02)

- Stub-hidden (Tier A `>1.02x`): `type_is_subtype`. Still `cpdef`.

