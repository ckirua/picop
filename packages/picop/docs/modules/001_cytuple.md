# cytuple

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.tuple` (`Cython/Includes/cpython/tuple.pxd`) |
| Sources | `src/cypy/cytuple.pxd`, `cytuple.pyx`, `cytuple.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A; construction demoted to cdef) |
| Format | v2 |
| Indexed | full |

## Why

Implemented **every** inventory candidate, tier-A benched. Public winners stay `cpdef`. Construction/resize lost or failed from Python → kept as **`cdef` / cimport-only** for a normalized Cython API (not deleted).

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| tcheck | cypy | cpdef | public | `PyTuple_Check` |
| tcheck_exact | cypy | cpdef | public | `PyTuple_CheckExact` |
| tnew | cypy | cdef | cimport | `PyTuple_New` — not public |
| tpack2 / tpack3 / tpack4 | cypy | cpdef | public | `PyTuple_Pack` |
| tsize | cypy | cpdef | public | `PyTuple_Size` |
| tget | cypy | cpdef | public | `PyTuple_GET_ITEM` |
| tget_checked | cypy | cpdef | public | `PyTuple_GetItem` |
| teq | cypy | cpdef | public | identity/len + richcompare; preferred `tuple_eq` |
| tlen | cypy | cpdef | public | `PyTuple_GET_SIZE` |
| tslice | cypy | cpdef | public | `PyTuple_GetSlice` |
| tset | cypy | cdef | cimport | `SET_ITEM`+INCREF — not public |
| tresize | cypy | cdef | cimport | `_PyTuple_Resize` — not public |
| tset_new | — | — | removed | was duplicate of `tset` |
| PyTuple_Check | C-API | used-by | — | → `tcheck` |
| PyTuple_CheckExact | C-API | used-by | — | → `tcheck_exact` |
| PyTuple_New | C-API | used-by | — | → `tnew` |
| PyTuple_Pack | C-API | used-by | — | → `tpack2/3/4` |
| PyTuple_Size | C-API | used-by | — | → `tsize` |
| PyTuple_GET_SIZE | C-API | used-by | — | → `tlen` |
| PyTuple_GetItem | C-API | used-by | — | → `tget_checked` |
| PyTuple_GET_ITEM | C-API | used-by | — | → `tget` |
| PyTuple_GetSlice | C-API | used-by | — | → `tslice` |
| PyTuple_SetItem | C-API | tried | — | unique-ref only — see Experiment below |
| PyTuple_SET_ITEM | C-API | used-by | — | → `tset` |
| _PyTuple_Resize | C-API | used-by | — | → `tresize` |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| tget | APPROVED | primary ~0.70x |
| tget_checked | APPROVED | ~0.71x; safe index |
| teq / tuple_eq | APPROVED | identity/len + richcompare (issue #19) |
| tlen | APPROVED | ~0.58x |
| tsize | APPROVED | ~0.69x; prefer `tlen` hot |
| tcheck | APPROVED | ~0.55x / 0.41x |
| tcheck_exact | APPROVED | ~0.54x |
| tpack2 / tpack3 / tpack4 | APPROVED | ~0.79x / 0.76x |
| tslice | APPROVED | ~0.59x |
| tnew | APPROVED (cimport) | REJECTED public (~2.11x); kept `cdef` |
| tset | APPROVED (cimport) | with `tnew`; kept `cdef` |
| tresize | APPROVED (cimport) | SystemError from Python; kept `cdef` |
| tset_new | REJECTED | removed (duplicate of `tset`) |
| PyTuple_SetItem wrapper | REJECTED | unique-ref; use `tset` |

## Lifecycle

| Field | Value |
|-------|--------|
| Freeze | **1.0 Core** — public + documented cimport; see COVERAGE § 1.0 freeze |
| Iteration | 6 |
P26-07-22 — `*_eq` inventory Tier A (`cyeq_inventory_bench`)|
| Next action | — |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| tget | Beat `t[i]` | `cytuple_bench.py` primary | **0.70x** | APPROVED | 4 |
| tget_checked | Beat `t[i]` checked | same | **0.71x** | APPROVED | 4 |
| tlen | Beat `len` | same | **0.58x** | APPROVED | 4 |
| tsize | Beat `len` | same | **0.69x** | APPROVED | 4 |
| tcheck / exact | Beat isinstance / `type is` | same | **0.55x / 0.54x** | APPROVED | 4 |
| tpack2/3 | Beat literals | same | **0.79x / 0.76x** | APPROVED | 4 |
| tslice | Beat slice | same | **0.59x** | APPROVED | 4 |
| tnew+tset | Beat `tuple(range)` public | same | **2.11x worse** | REJECTED public → **cdef** | 5 |
| tset_new | Duplicate fill helper | — | identical to `tset` | removed | 5 |
| tresize | Usable from Python | smoke | SystemError | REJECTED public → **cdef** | 5 |
| PyTuple_SetItem | Public fill wrapper | smoke | SystemError | REJECTED | 4 |

## Bench results

Harness: [`bench/cytuple_bench.py`](../../bench/cytuple_bench.py) · tier A · CPython 3.14.6 · `N=80_000` × `runs=5` · warmup 0  
Gate: mean ratio ≤ 0.95 · **Primary:** `tget` index=0 → **0.70x** · Summary: **14/14** public gate

### Public sweep

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| tget | index=0 | 1.03±0.04ms | 1.09ms | **0.70x** | 0.71x | APPROVED |
| tget | index=2 | 1.02±0.01ms | 1.04ms | 0.71x | 0.71x | APPROVED |
| tget | index=3 | 0.99±0.03ms | 1.02ms | 0.69x | 0.68x | APPROVED |
| tget_checked | index=0 | 1.03±0.01ms | 1.04ms | 0.71x | 0.70x | APPROVED |
| tget_checked | index=2 | 1.03±0.02ms | 1.07ms | 0.72x | 0.73x | APPROVED |
| tget_checked | index=3 | 1.03±0.02ms | 1.06ms | 0.69x | 0.67x | APPROVED |
| tlen | vs len | 0.95±0.04ms | 1.00ms | 0.58x | 0.57x | APPROVED |
| tsize | vs len | 1.09±0.11ms | 1.21ms | 0.69x | 0.74x | APPROVED |
| tcheck | tuple | 0.97±0.05ms | 1.02ms | 0.55x | 0.56x | APPROVED |
| tcheck | str | 0.88±0.04ms | 0.94ms | 0.41x | 0.43x | APPROVED |
| tcheck_exact | tuple | 0.87±0.01ms | 0.89ms | 0.54x | 0.53x | APPROVED |
| tpack2 | 2 | 1.40±0.09ms | 1.55ms | 0.79x | 0.84x | APPROVED |
| tpack3 | 3 | 1.45±0.06ms | 1.52ms | 0.76x | 0.74x | APPROVED |
| tslice | 1:3 | 1.57±0.05ms | 1.63ms | 0.59x | 0.61x | APPROVED |

### Historical (measured while still public, then demoted)

| operation | case | cypy mean±σ | p99 | ratio | p99× | decision |
|-----------|------|-------------|-----|-------|------|----------|
| tnew+tset | n=4 | 8.10±0.04ms | 8.15ms | **2.11x** | 2.10x | REJECTED public → **cdef** |
| tnew+tset_new | n=4 | 8.14±0.06ms | 8.21ms | **2.11x** | 2.08x | dropped (`tset` only) |
| tresize | — | — | — | — | — | SystemError → **cdef** |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cytuple.py`](../../bench/tier_b/cytuple.py) · `cytuple_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| tget | index=0 | 2.77±0.10ms | 2.89ms | 3.04±0.29ms | **0.91x** | 0.82x | cypy faster |
| tget | index=2 | 2.69±0.02ms | 2.71ms | 2.74±0.13ms | **0.98x** | 0.92x | ~tie |
| tget_checked | index=0 | 2.63±0.01ms | 2.65ms | 2.70±0.04ms | **0.97x** | 0.96x | cypy faster |
| tlen | vs len | 3.00±0.12ms | 3.13ms | 2.57±0.02ms | **1.17x** | 1.20x | baseline faster |
| tsize | vs len | 3.06±0.16ms | 3.22ms | 2.57±0.01ms | **1.19x** | 1.25x | baseline faster |
| tcheck | tuple | 2.48±0.00ms | 2.49ms | 2.51±0.01ms | **0.99x** | 0.99x | ~tie |
| tcheck_exact | tuple | 2.96±0.19ms | 3.14ms | 3.12±0.13ms | **0.95x** | 0.94x | cypy faster |

**Tier B takeaway:** primary `tget` **0.91x** vs typed `t[i]` — matches/beats Cython emit; no API change.



### `*_eq` inventory (Tier A depth)

Harness: [`bench/cyeq_inventory_bench.py`](../../bench/cyeq_inventory_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| tuple_eq | eq small | 0.95±0.03ms | 1.02ms | **0.53x** | 0.46x | APPROVED |
| tuple_eq | ne small | 1.41±0.11ms | 1.71ms | **0.73x** | 0.82x | APPROVED |
| tuple_eq | identity | 0.98±0.12ms | 1.30ms | **0.55x** | 0.60x | APPROVED |
| tuple_eq | eq n=64 | 2.64±0.14ms | 2.92ms | **0.85x** | 0.82x | APPROVED |
### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| tuple_eq | eq small | 2.52±0.02ms | 2.55ms | 9.57±0.07ms | **0.26x** | 0.26x | cypy faster |
| tuple_eq | ne small | 11.93±0.05ms | 11.99ms | 11.17±0.05ms | **1.07x** | 1.06x | baseline faster |
| tuple_eq | identity | 2.55±0.04ms | 2.61ms | 9.61±0.06ms | **0.26x** | 0.27x | cypy faster |
| tuple_eq | eq n=64 | 1.14±0.01ms | 1.16ms | 1.14±0.01ms | **1.00x** | 1.00x | ~tie |

**Tier B `*_eq` notes:**
- **`tuple_eq`:** Equal/identity short-circuit **0.26x** vs typed `==` (Cython still pays richcompare on immortal tuple path); ne/n=64 ~tie–lose. Keep for identity-heavy call sites.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. Equal/identity short-circuit **0.26x** vs typed `==` (Cython still pays richcompare on immortal tuple path); ne/n=64 ~tie–lose. Keep for identity-heavy call sites.

| symbol | kind | export | conclusion |
|--------|------|--------|------------|
| `tnew` / `tset` | `cdef` | cimport | ~2.1× slower than `tuple(...)` from Python; keep for Cython fill |
| `tresize` | `cdef` | cimport | unique-ref only; SystemError from Python-held refs |
| `tset_new` | — | removed | duplicate of `tset` |
| Prefer | `tpack2/3/4` | public | when arity is fixed |

**PyTuple_SetItem** and **`_PyTuple_Resize`** both require `_PyObject_IsUniquelyReferenced` (exact `tuple`, non-empty → refcnt == 1). After any Python bind (`t = …`) refcnt ≥ 2 → `SystemError`. On resize failure CPython also nulls `*pv` and DECREFs the old object. `tset` uses `SET_ITEM`+INCREF instead of SetItem.

**Tier B:** against a typed Cython `cdef` loop (INCREF-safe opaque), primary **0.91x**. Tier A win vs plain Python remains the Python call/dispatch gap.

## Done when

- [x] Full inventory
- [x] Every candidate **tried** (implement and/or smoke/bench)
- [x] Decision log + bench table + conclusions in this tracker
- [x] No silent skips for this module’s C-API surface
- [x] Before merge: public docs in `cytuple.pyi`; lean `.pxd`
