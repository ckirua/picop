# cyfloat

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.float` |
| Sources | `src/cypy/cyfloat.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Float type checks and C `double` bridge. From Python, `float()` often wins; helpers matter for typed Cython.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| float_check / exact | public | |
| float_eq | public | float/float C `==`; else RichCompare; soft `feq` |
| float_from_double / from_string / as_double | public | |
| float_as_double_unchecked | cimport | `AS_DOUBLE` macro |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| float_check* | APPROVED | **0.41–0.57x** |
| feq / float_eq | APPROVED | C `double ==` / RichCompare (issue #27); not on `hot` |
| float_from_string | APPROVED (API) | **1.03x** ~tie |
| float_from_double / as_double | APPROVED (API) | **1.30–1.53x** — C bridge |
| AS_DOUBLE unchecked | APPROVED (cimport) | no type check |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
P26-07-22 — `*_eq` inventory Tier A (`cyeq_inventory_bench`)|
| Next action | — |

## Decision log

| Function | Result | Decision | Iteration |
|----------|--------|----------|-----------|
| float_check | 0.41–0.52x | APPROVED | 1 |
| from/as | 1.03–1.53x | APPROVED (API) | 1 |
| feq / float_eq | float/float C `==`; else RichCompare; NaN/−0 Python parity | APPROVED | 1 |

## Bench notes

- Harness: [`bench/cyfloat_bench.py`](../../bench/cyfloat_bench.py) · N=80000

## Bench results

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| float_check | float / int | 0.52x / 0.41x | pass |
| float_check_exact | float | 0.57x | pass |
| float_from_double | 2.5 | 1.35x | API |
| float_from_string | '2.5' | 1.03x | API |
| float_as_double | pi / int | 1.53x / 1.30x | API |

Summary: 3/7 gate · mean **0.96x**.

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cyfloat.py`](../../bench/tier_b/cyfloat.py) · `cyfloat_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| float_check | hit | 2.86±0.11ms | 3.02ms | 2.86±0.19ms | **1.00x** | 0.99x | ~tie |

**Tier B takeaway:** primary `float_check` **1.00x** vs typed Cython baseline (hit).



### `*_eq` inventory (Tier A depth)

Harness: [`bench/cyeq_inventory_bench.py`](../../bench/cyeq_inventory_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| float_eq | eq | 1.01±0.03ms | 1.06ms | **0.67x** | 0.67x | APPROVED |
| float_eq | ne | 1.03±0.06ms | 1.12ms | **0.68x** | 0.70x | APPROVED |
### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| float_eq | eq | 2.58±0.04ms | 2.62ms | 5.05±0.04ms | **0.51x** | 0.51x | cypy faster |
| float_eq | ne | 2.56±0.02ms | 2.59ms | 5.02±0.02ms | **0.51x** | 0.51x | cypy faster |

**Tier B `*_eq` notes:**
- **`float_eq`:** **0.51x** win vs Cython `float == float`.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. **0.51x** win vs Cython `float == float`.

**Tier B:** `float_check` **0.99x** vs isinstance — ~parity.

| Topic | Finding |
|-------|---------|
| Check win | Type-slot vs isinstance |
| Why as/from lose | `float` builtin specializes; still needed for `double` in Cython |
| AS_DOUBLE | Unchecked — crash on non-float |
| Why Check wins | Type slot vs isinstance |
| Why From/As lose | Python float specialize small constants; C-API pays conversion framing (~1.3–1.5x) |
| Safety | AsDouble on non-float uses number protocol — may call `__float__` and set errors |
| Scale | String parse ~tie with `float('2.5')` (1.04x) |
| `float_eq` | Float/float: C `double ==` (NaN != NaN, `+0.0 == -0.0`). Mixed: `PyObject_RichCompare` — **not** `RichCompareBool` (identity-shortcuts same-object NaN → True). Leave off `hot` |


## Done when

- [x] Try-all + depth + benches + `.pyi`

### Stub visibility (2026-08-02)

- Stub-hidden (Tier A `>1.02x`): `float_from_double`, `float_from_cstr`, `float_as_double`. Still `cpdef`.

