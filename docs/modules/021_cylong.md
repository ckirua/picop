# cylong

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.long` |
| Sources | `src/cypy/cylong.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

C↔`int` bridge and exactness checks (`bool` is a long subtype). From Python, `int()`/`float()` often beat boxed helpers — keep as API for Cython call sites.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| long_check / exact | public | Exact rejects `bool` |
| long_eq / int_eq | public | identity + richcompare; preferred `long_eq`; `int_eq` alias |
| long_from_* (long/ulong/ssize/size/ll/ull/double) | public | C constructors |
| long_as_* / masks / double | public | |
| long_as_long_overflow | public | `(value, overflow)` tuple |
| long_from_string / voidptr / as_voidptr / as_ll_overflow | cimport | pointers / out-param |
| FromUnicode | REJECTED | deprecated path in include |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| long_check* | APPROVED | **0.44–0.52x** |
| loeq / long_eq / int_eq | APPROVED | identity + richcompare (issue #25); not on `hot` |
| long_as_long_overflow | APPROVED | **0.73x** |
| long_from_* / long_as_* | APPROVED (API) | **1.14–1.40x** vs `int`/`float` — Cython C bridge |
| string/voidptr/ll_overflow cdef | APPROVED (cimport) | |
| FromUnicode | REJECTED | deprecated |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
P26-07-22 — `*_eq` inventory Tier A (`cyeq_inventory_bench`)|
| Next action | — |

## Decision log

| Function | Result | Decision | Iteration |
|----------|--------|----------|-----------|
| long_check_exact vs bool | 0.52x; False for True | APPROVED | 1 |
| from/as vs int() | 1.14–1.40x lose | APPROVED (API) | 1 |
| overflow tuple | 0.73x | APPROVED | 1 |
| loeq / long_eq / int_eq | identity + richcompare; API symmetry | APPROVED | 1 |

## Bench notes

- Harness: [`bench/cylong_bench.py`](../../bench/cylong_bench.py) · N=80000

## Bench results

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| long_check | int / bool | 0.49x / 0.44x | pass |
| long_check_exact | int / bool | 0.52x / 0.52x | pass |
| long_from_long / ssize / double | | 1.14–1.40x | API |
| long_as_long / ssize / double | | 1.14–1.28x | API |
| long_as_long_overflow | small | 0.73x | pass |

Summary: 5/11 gate · mean **0.93x**.

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cylong.py`](../../bench/tier_b/cylong.py) · `cylong_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| long_check | hit | 2.46±0.01ms | 2.47ms | 2.47±0.00ms | **1.00x** | 1.00x | ~tie |

**Tier B takeaway:** primary `long_check` **1.00x** vs typed Cython baseline (hit).



### `*_eq` inventory (Tier A depth)

Harness: [`bench/cyeq_inventory_bench.py`](../../bench/cyeq_inventory_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| long_eq | eq small | 0.90±0.02ms | 0.94ms | **0.59x** | 0.57x | APPROVED |
| long_eq | ne | 1.15±0.03ms | 1.19ms | **0.78x** | 0.77x | APPROVED |
| long_eq | eq big | 1.24±0.05ms | 1.32ms | **0.72x** | 0.74x | APPROVED |
| int_eq | eq | 0.94±0.06ms | 1.08ms | **0.63x** | 0.69x | APPROVED |
### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| long_eq | eq small | 2.51±0.02ms | 2.53ms | 5.79±0.09ms | **0.43x** | 0.43x | cypy faster |
| long_eq | ne | 5.18±0.04ms | 5.24ms | 5.74±0.02ms | **0.90x** | 0.91x | cypy faster |
| long_eq | eq big | 6.75±0.03ms | 6.78ms | 6.57±0.05ms | **1.03x** | 1.02x | baseline faster |
| int_eq | eq | 2.83±0.71ms | 4.04ms | 5.80±0.05ms | **0.49x** | 0.69x | cypy faster |

**Tier B `*_eq` notes:**
- **`long_eq`:** Small eq **0.43x**; ne **0.90x**; big int ~tie (**1.03x**) — digit compare dominates.
- **`int_eq`:** **0.49x** win (alias of long path).

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. Small eq **0.43x**; ne **0.90x**; big int ~tie (**1.03x**) — digit compare dominates.

**Tier B:** `long_check` **1.00x** vs isinstance — ~parity.

| Topic | Finding |
|-------|---------|
| Check win | Fast type check; exact separates `bool` |
| Why from/as lose | Small-int immortal / `int()` bytecode specializes; helpers still needed for typed C args in Cython |
| Overflow | Tuple wrapper avoids manual out-param from Python |
| Masks | Wrap without exception — document wraparound |
| Why win | Check/Exact beat isinstance; overflow-checked AsLong wins when exception path matters |
| Scale | FromLong/AsLong lose ~1.2x to Python int boxing specializing small ints |
| Safety | `AsLongAndOverflow` sets overflow flag — must read flag, not only return value |
| Subtype | bool is int subclass: Check true, Exact false — matches CPython |
| `long_eq` | Same semantics as `==` (identity then richcompare); `int_eq` thin alias; measured; leave off `hot` (prefer specialized paths / clarity) |


## Done when

- [x] Try-all + depth + benches + `.pyi`

### Stub visibility (2026-08-02)

- Stub-hidden (Tier A `>1.02x`): `long_from_long`, `long_from_ssize`, `long_from_double`, `long_as_long`, `long_as_ssize`, `long_as_double`. Still `cpdef`.

