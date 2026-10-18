# cynumber

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.number` |
| Sources | `src/cypy/cynumber.pxd`, `.pyx`, `.pyi` |
| Surface | public |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Abstract number protocol for unknown concrete types. Prefer typed modules (`cylong`/`cyfloat`) when known — binary ops lose to `operator.*` from Python.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| num_check / num_index_check | public | |
| num_eq | public | RichCompare; soft `neq_num`; prefer typed `*_eq` |
| binary / unary / inplace / convert | public (cpdef) | Tier A losers stub-hidden from `.pyi` when `> 1.02x` |
| PyNumber_Divide / InPlaceDivide / Coerce | — | REJECTED (ABI missing 3.14) |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| num_check / index_check | APPROVED | **0.30–0.45x** |
| num_inplace_add | APPROVED | **0.78x** |
| num_eq / neq_num | APPROVED | RichCompare (issue #29); not on `hot` |
| binary / unary / convert | APPROVED (API) | **1.07–1.34x** — protocol completeness; stub-hidden when Tier A `> 1.02x` |
| stub visibility | checks + wins | `.pyi` keeps `num_check*` / `num_eq` / `num_floordiv` / `num_inplace_add` (+ unmeasured) |
| Divide / InPlaceDivide / Coerce | REJECTED | missing from libpython3.14 |

## Lifecycle

| Field | Value |
|-------|--------|
| Freeze | **Provisional (Protocols)** after 1.0 — not Core; may evolve under minors |
| Iteration | 1 |
| Last pass | 2026-08-02 — stub-hide Tier A `>1.02x` from `.pyi` |
| Next action | — |

## Decision log

| Function | Result | Decision | Iteration |
|----------|--------|----------|-----------|
| checks | 0.30–0.45x | APPROVED | 1 |
| ops | 1.07–1.34x | APPROVED (API) | 1 |
| inplace_add | 0.78x | APPROVED | 1 |
| Divide/Coerce | ctypes missing | REJECTED | 1 |
| neq_num / num_eq | RichCompare; NaN parity; protocol bridge | APPROVED | 1 |

## Bench notes

- Harness: [`bench/cynumber_bench.py`](../../bench/cynumber_bench.py) · N=80000

## Bench results

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| num_check | int / str | 0.30x / 0.33x | pass |
| num_index_check | int / float | 0.31x / 0.45x | pass |
| num_add / mul / … | ints | 1.07–1.17x | API |
| num_inplace_add | 10+=3 | 0.78x | pass |
| num_as_ssize | 99 | 1.34x | API |

Summary: 5/17 gate · mean **0.94x**.

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cynumber.py`](../../bench/tier_b/cynumber.py) · `cynumber_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| num_check | hit | 3.22±0.16ms | 3.36ms | 2.60±0.13ms | **1.24x** | 1.21x | baseline faster |

**Tier B takeaway:** primary `num_check` **1.24x** vs typed Cython baseline (hit).



### `*_eq` inventory (Tier A depth)

Harness: [`bench/cyeq_inventory_bench.py`](../../bench/cyeq_inventory_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| num_eq | int↔float | 1.35±0.02ms | 1.39ms | **0.71x** | 0.69x | APPROVED |
| num_eq | ne | 1.11±0.04ms | 1.18ms | **0.73x** | 0.70x | APPROVED |
### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| num_eq | int↔float | 12.26±0.04ms | 12.29ms | 11.95±0.05ms | **1.03x** | 1.02x | baseline faster |
| num_eq | ne | 6.17±0.04ms | 6.22ms | 5.76±0.02ms | **1.07x** | 1.08x | baseline faster |

**Tier B `*_eq` notes:**
- **`num_eq`:** Slight lose (**1.03–1.07x**) — numeric coerce path; prefer typed `long_eq`/`float_eq` when known.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. Slight lose (**1.03–1.07x**) — numeric coerce path; prefer typed `long_eq`/`float_eq` when known.

**Tier B:** `num_check` **1.29x** vs isinstance tuple — Cython emit tighter for multi-type check.

| Topic | Finding |
|-------|---------|
| Check win | Slot probe vs hasattr/`__index__` |
| Why ops lose | `operator.add` etc. specialize; `PyNumber_*` is abstract nb_* dispatch |
| Prefer typed | Use `long_*` / `float_*` when type known |
| InPlace | Wins when avoiding Python `+=` bytecode for immutable ints (returns new) |
| ABI | `PyNumber_Divide` / `InPlaceDivide` / `Coerce` removed — ctypes AttributeError |
| Cheap aliases | All InPlace* siblings wrapped |
| `num_eq` | Abstract `==` via `PyObject_RichCompare` (not `RichCompareBool` — identity-shortcuts same-object NaN → True). Prefer `long_eq`/`float_eq`/`complex_eq`/`bool_eq` when typed. Soft `neq_num`. Leave off `hot` (protocol bridge / clarity). Errors from `__eq__` propagate; `NotImplemented` on both sides → False for EQ (CPython `do_richcompare`) |

## Done when

- [x] Try-all + depth + benches + `.pyi`

### Ops remaining inventory (Tier A)

Harnesses: [`bench/cyaccessors_inventory_bench.py`](../../bench/cyaccessors_inventory_bench.py) / [`bench/cyruntime_inventory_bench.py`](../../bench/cyruntime_inventory_bench.py). See [`OPS_INVENTORY.md`](../OPS_INVENTORY.md) + [`OPS_INVENTORY_TIERB.md`](../OPS_INVENTORY_TIERB.md) for status / Tier B n/a.
