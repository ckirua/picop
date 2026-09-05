# cylist

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.list` (`Cython/Includes/cpython/list.pxd`) |
| Sources | `src/cypy/cylist.pxd`, `cylist.pyx`, `cylist.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Hot-path get/append/len/slice for typed exact `list`, plus full include try-all. Depth covered unchecked get, NULL-slot `lnew`, SetItem steal+INCREF, and subtype typing (same Cython `list` exactness as `dict`/`tuple`).

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| lcheck | cypy | cpdef | public | `PyList_Check` |
| lcheck_exact | cypy | cpdef | public | `PyList_CheckExact` |
| lempty | cypy | cpdef | public | `PyList_New(0)` |
| lnew | cypy | cdef | cimport | `PyList_New(n)` — NULL slots |
| lget | cypy | cpdef | public | `PyList_GET_ITEM` unchecked |
| lget_checked | cypy | cpdef | public | `PyList_GetItem` |
| lget_ref | cypy | cpdef | public | `PyList_GetItemRef` |
| leq | cypy | cpdef | public | identity/len + richcompare; preferred `list_eq` |
| llen | cypy | cpdef | public | `PyList_GET_SIZE` — exact `list` |
| lsize | cypy | cpdef | public | `PyList_Size` — subtypes OK |
| lappend | cypy | cpdef | public | `PyList_Append` |
| linsert | cypy | cpdef | public | `PyList_Insert` |
| lextend | cypy | cpdef | public | `PyList_Extend` |
| lclear | cypy | cpdef | public | `PyList_Clear` |
| lcopy | cypy | cpdef | public | full `GetSlice` |
| lslice | cypy | cpdef | public | `PyList_GetSlice` |
| lset_slice | cypy | cpdef | public | `PyList_SetSlice` (`None` deletes) |
| lsort | cypy | cpdef | public | `PyList_Sort` |
| lreverse | cypy | cpdef | public | `PyList_Reverse` |
| las_tuple | cypy | cpdef | public | `PyList_AsTuple` |
| lset_item | cypy | cpdef | public | `SetItem` + INCREF |
| lset | cypy | cdef | cimport | `SET_ITEM` + INCREF (fill `lnew`) |
| PyList_* | C-API | used-by | — | all include symbols mapped above |
| `_PyList_*` private | C-API | tried | — | not wrapped |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| lget | APPROVED | primary **0.68x** |
| lget_checked | APPROVED | **0.70x** |
| lget_ref | APPROVED | **0.67x** |
| leq / list_eq | APPROVED | identity/len + richcompare (issue #18) |
| llen / lsize | APPROVED | **0.58x** / **0.59x** |
| lcheck / exact | APPROVED | **0.51x** / **0.58x** |
| lempty | APPROVED | **0.75x** vs `[]` |
| lappend / linsert / lextend / lclear / lcopy | APPROVED | 0.87–0.94x |
| lset_item | APPROVED | **0.99x** tie — API-clarity keep |
| lset_slice / lsort / lreverse | APPROVED | 0.89–0.92x |
| lslice | APPROVED | **0.65x** |
| las_tuple | APPROVED | **0.71x** small / **0.91x** n=64 |
| lnew / lset | APPROVED (cimport) | NULL-slot construction; fill before expose |
| `_PyList_*` | REJECTED | private |

## Lifecycle

| Field | Value |
|-------|--------|
| Freeze | **1.0 Core** — public + documented cimport; see COVERAGE § 1.0 freeze |
| Iteration | 1 |
P26-07-22 — `*_eq` inventory Tier A (`cyeq_inventory_bench`)|
| Next action | — |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| lget | Beat `l[i]` | `bench/cylist_bench.py` | **0.68x** | APPROVED | 1 |
| lget_checked / lget_ref | Safe / strong get | same | 0.70x / 0.67x | APPROVED | 1 |
| llen / lsize / checks / lempty | Macro/C-API | same | 0.51–0.75x | APPROVED | 1 |
| mutators + slice/sort/reverse/as_tuple | Hot helpers | same | 0.65–0.94x | APPROVED | 1 |
| lset_item | SetItem+INCREF | same | **0.99x** | APPROVED (clarity) | 1 |
| lnew / lset | Builder path | smoke/docs | NULL slots / SET_ITEM | APPROVED (cimport) | 1 |

## Bench notes

- Harness: [`bench/cylist_bench.py`](../../bench/cylist_bench.py)
- Primary: `lget` index=0 on small list
- Env: CPython 3.14.6 · Linux x86_64 · GIL on (venv bench) · N=80000 RUNS=5

## Bench results

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| lget | index=0 | 1.01±0.06ms | 1.10ms | 0.68x | 0.72x | pass |
| lget | index=3 | 0.96±0.01ms | 0.97ms | 0.64x | 0.63x | pass |
| lget | n=64 mid | 1.00±0.04ms | 1.06ms | 0.68x | 0.69x | pass |
| lget_checked | index=0 | 1.03±0.02ms | 1.05ms | 0.70x | 0.70x | pass |
| lget_ref | index=0 | 1.01±0.03ms | 1.07ms | 0.67x | 0.66x | pass |
| llen | small | 0.94±0.02ms | 0.97ms | 0.58x | 0.58x | pass |
| llen | n=64 | 0.94±0.02ms | 0.96ms | 0.58x | 0.56x | pass |
| lsize | small | 0.96±0.03ms | 1.00ms | 0.59x | 0.59x | pass |
| lcheck | list | 0.91±0.04ms | 0.98ms | 0.51x | 0.54x | pass |
| lcheck_exact | exact | 0.94±0.05ms | 0.99ms | 0.58x | 0.59x | pass |
| lempty | empty | 1.31±0.05ms | 1.39ms | 0.75x | 0.79x | pass |
| lappend | append | 3.15±0.10ms | 3.30ms | 0.94x | 0.96x | pass |
| linsert | insert | 3.25±0.05ms | 3.30ms | 0.87x | 0.86x | pass |
| lextend | extend | 3.33±0.09ms | 3.45ms | 0.90x | 0.92x | pass |
| lclear | clear | 3.03±0.06ms | 3.13ms | 0.90x | 0.89x | pass |
| lcopy | small | 2.54±0.04ms | 2.60ms | 0.89x | 0.89x | pass |
| lset_item | set | 3.19±0.08ms | 3.31ms | 0.99x | 1.02x | tie / keep |
| lset_slice | slice assign | 4.57±0.10ms | 4.68ms | 0.89x | 0.91x | pass |
| lsort | n=3 | 3.83±0.07ms | 3.89ms | 0.92x | 0.91x | pass |
| lreverse | n=3 | 2.97±0.08ms | 3.10ms | 0.91x | 0.94x | pass |
| lslice | n=64 mid10 | 2.01±0.05ms | 2.06ms | 0.65x | 0.65x | pass |
| las_tuple | small | 1.44±0.02ms | 1.46ms | 0.71x | 0.71x | pass |
| las_tuple | n=64 | 5.99±0.02ms | 6.02ms | 0.91x | 0.91x | pass |

Summary: 23/23 faster · 22/23 ≥5% gate · mean ratio **0.76x** · median **0.71x**.

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cylist.py`](../../bench/tier_b/cylist.py) · `cylist_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| lget | index=0 | 2.51±0.02ms | 2.53ms | 2.56±0.05ms | **0.98x** | 0.96x | cypy faster |
| lget_checked | index=0 | 2.94±0.18ms | 3.12ms | 2.54±0.00ms | **1.16x** | 1.23x | baseline faster |
| llen | n=4 | 2.94±0.08ms | 3.02ms | 2.93±0.18ms | **1.01x** | 0.97x | ~tie |
| lcheck | list | 2.50±0.03ms | 2.54ms | 2.51±0.01ms | **0.99x** | 1.01x | ~tie |

**Tier B takeaway:** primary `lget` **0.98x** vs typed `l[i]` — ~parity with Cython emit.


### `*_eq` inventory (Tier A depth)

Harness: [`bench/cyeq_inventory_bench.py`](../../bench/cyeq_inventory_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| list_eq | eq small | 1.42±0.11ms | 1.70ms | **0.74x** | 0.76x | APPROVED |
| list_eq | ne small | 1.54±0.10ms | 1.79ms | **0.73x** | 0.78x | APPROVED |
| list_eq | identity | 1.02±0.11ms | 1.30ms | **0.54x** | 0.59x | APPROVED |
| list_eq | eq n=64 | 3.37±0.13ms | 3.70ms | **0.86x** | 0.88x | APPROVED |
### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| list_eq | eq small | 12.02±0.87ms | 12.95ms | 11.29±0.46ms | **1.07x** | 1.10x | baseline faster |
| list_eq | ne small | 12.04±0.06ms | 12.14ms | 11.96±0.12ms | **1.01x** | 1.00x | ~tie |
| list_eq | identity | 2.52±0.01ms | 2.53ms | 10.74±0.05ms | **0.23x** | 0.23x | cypy faster |
| list_eq | eq n=64 | 1.46±0.02ms | 1.50ms | 1.48±0.04ms | **0.99x** | 0.97x | ~tie |

**Tier B `*_eq` notes:**
- **`list_eq`:** Identity short-circuit wins hard (**0.23x**); equal/ne elementwise ~tie–lose vs typed Cython `==` (richcompare dominates). Tier A win remains Python call overhead.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. Identity short-circuit wins hard (**0.23x**); equal/ne elementwise ~tie–lose vs typed Cython `==` (richcompare dominates). Tier A win remains Python call overhead.

**Tier B:** primary `lget` **0.98x** vs typed `l[i]` — ~parity with Cython emit.

| Topic | Finding |
|-------|---------|
| Why `lget` wins | Macro `GET_ITEM` skips bound-method / abstract index path |
| Unchecked get | `lget` has **no** bounds check — OOB is UB; use `lget_checked` / `lget_ref` when unsure |
| `lnew` | `PyList_New(n)` for `n>0` leaves **NULL** item slots — must `lset` before exposing to Python (same class of hazard as `tnew` / `bnew`) |
| `lset` vs `lset_item` | `SET_ITEM` does not DECREF old (fill-only); `SetItem` steals and DECREFs previous — public path INCREFs then `SetItem` |
| Exact `list` typing | Cython typed `list` rejects subtypes (`TypeError` on `llen`); use `lsize` / `lcheck` for subclasses |
| `lset_slice(None)` | Must pass C **NULL** (not Python `None` as object) — wrapper maps `None` → NULL for `del l[i:j]` |
| `_PyList_*` | Present on 3.14 `.so`; private → REJECTED |

## Done when

- [x] Full inventory vs `cpython.list`
- [x] Try-all + **depth** (unchecked get, NULL slots, SetItem steal, subtypes)
- [x] Bench results + experiment conclusions in **this** file
- [x] Before merge: `.pyi` one-liners; lean `.pxd`; `lnew`/`lset` not public
