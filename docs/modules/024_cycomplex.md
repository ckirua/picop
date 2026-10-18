# cycomplex

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.complex` |
| Sources | `src/cypy/cycomplex.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Complex type checks and C `double` real/imag bridge. From Python, attribute access often loses to C-API; helpers matter for typed Cython and `Py_complex`.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| complex_check / exact | public | |
| complex_eq | public | complex/complex C `==` on real/imag; else RichCompare; soft `ceq` |
| complex_from_doubles | public | |
| complex_real_as_double / imag_as_double | public | |
| complex_from_ccomplex / as_ccomplex | cimport | `Py_complex` |
| Py_complex | cimport | struct type |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| complex_check* | APPROVED | **0.43–0.56x** |
| ceq / complex_eq | APPROVED | C `double ==` on parts / RichCompare (issue #28); not on `hot` |
| complex_from_doubles | APPROVED | **0.75x** |
| complex_real/imag_as_double | APPROVED | **0.60–0.61x** on complex; int path **1.55x** API keep |
| FromCComplex / AsCComplex | APPROVED (cimport) | `Py_complex` only |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
P26-07-22 — `*_eq` inventory Tier A (`cyeq_inventory_bench`)|
| Next action | — |

## Decision log

| Function | Result | Decision | Iteration |
|----------|--------|----------|-----------|
| complex_check* | 0.43–0.56x | APPROVED | 1 |
| from_doubles | 0.75x | APPROVED | 1 |
| real/imag | 0.60–0.61x | APPROVED | 1 |
| CComplex | struct | APPROVED (cimport) | 1 |
| ceq / complex_eq | complex/complex C `==` on parts; else RichCompare; NaN/−0 Python parity | APPROVED | 1 |

## Bench notes

- Harness: [`bench/cycomplex_bench.py`](../../bench/cycomplex_bench.py) · N=80000

## Bench results

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| complex_check | complex / int / subtype | 0.51x / 0.43x / 0.50x | pass |
| complex_check_exact | complex / subtype | 0.56x / 0.54x | pass |
| complex_from_doubles | 1.5+2.5j | 0.75x | pass |
| complex_real_as_double | Z.real / int 7 | 0.61x / 1.55x | pass / API |
| complex_imag_as_double | Z.imag | 0.60x | pass |

Summary: 8/9 gate · mean **0.67x**.

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cycomplex.py`](../../bench/tier_b/cycomplex.py) · `cycomplex_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| complex_check | hit | 2.91±0.09ms | 3.04ms | 3.00±0.14ms | **0.97x** | 0.96x | cypy faster |

**Tier B takeaway:** primary `complex_check` **0.97x** vs typed Cython baseline (hit).



### `*_eq` inventory (Tier A depth)

Harness: [`bench/cyeq_inventory_bench.py`](../../bench/cyeq_inventory_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| complex_eq | eq | 1.15±0.11ms | 1.31ms | **0.62x** | 0.66x | APPROVED |
| complex_eq | ne | 1.10±0.06ms | 1.26ms | **0.60x** | 0.65x | APPROVED |
### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| complex_eq | eq | 3.51±0.02ms | 3.52ms | 7.34±0.03ms | **0.48x** | 0.48x | cypy faster |
| complex_eq | ne | 3.52±0.04ms | 3.57ms | 7.32±0.02ms | **0.48x** | 0.49x | cypy faster |

**Tier B `*_eq` notes:**
- **`complex_eq`:** **0.48x** win vs Cython `complex == complex`.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. **0.48x** win vs Cython `complex == complex`.

**Tier B:** `complex_check` **0.93x** vs isinstance.

| Topic | Finding |
|-------|---------|
| Check win | Type-slot vs isinstance |
| real/imag win | Direct `cval` / C-API vs Python attr descriptor |
| Why int loses | `RealAsDouble` converts via number protocol; `float(7)` specializes |
| FromDoubles win | Avoids Python `complex` call overhead |
| CComplex | Error sentinel `(-1+0i)` — must check `PyErr_Occurred`; cdef only |
| Subtype | Check true / Exact false — matches `isinstance` vs `type is` |
| `complex_eq` | Complex/complex: C `double ==` on real and imag (NaN on either part => unequal, `+0.0 == -0.0`). Mixed: `PyObject_RichCompare` — **not** `RichCompareBool` (identity-shortcuts same-object NaN parts → True). Leave off `hot` |

## Done when

- [x] Try-all + depth + benches + `.pyi`
