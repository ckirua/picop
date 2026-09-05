# cydict

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.dict` (`Cython/Includes/cpython/dict.pxd`) + 3.13+ `PyDict_Pop*` / `ContainsString` |
| Sources | `src/cypy/cydict.pxd`, `cydict.pyx`, `cydict.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Hot-path get/set/pop/merge/len for typed exact `dict` + `str` keys, plus full include try-all. Depth covered borrowed vs strong-ref get, subtype typing, view materialization loss, and C-string key cost.

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| dcheck | cypy | cpdef | public | `PyDict_Check` |
| dcheck_exact | cypy | cpdef | public | `PyDict_CheckExact` |
| dnew | cypy | cpdef | public | `PyDict_New` |
| dproxy | cypy | cpdef | public | `PyDictProxy_New` |
| dget | cypy | cpdef | public | borrowed `PyDict_GetItem` |
| dget_with_error | cypy | cpdef | public | `PyDict_GetItemWithError` |
| dget_ref | cypy | cpdef | public | strong `PyDict_GetItemRef` |
| dcontains | cypy | cpdef | public | `PyDict_Contains` |
| dlen | cypy | cpdef | public | `PyDict_GET_SIZE` — **exact `dict` only** |
| deq | cypy | cpdef | public | identity/size + richcompare; preferred `dict_eq` |
| dsize | cypy | cpdef | public | `PyDict_Size` — accepts subtypes |
| dset | cypy | cpdef | public | `PyDict_SetItem` |
| ddel | cypy | cpdef | public | `PyDict_DelItem` |
| dpop | cypy | cpdef | public | `PyDict_Pop` (owns result ref) |
| dupdate | cypy | cpdef | public | `PyDict_Update` |
| dmerge | cypy | cpdef | public | `PyDict_Merge` + override flag |
| dmerge_from_seq2 | cypy | cpdef | public | `PyDict_MergeFromSeq2` |
| dsetdefault | cypy | cpdef | public | borrowed `PyDict_SetDefault` |
| dsetdefault_ref | cypy | cpdef | public | `PyDict_SetDefaultRef` |
| dclear | cypy | cpdef | public | `PyDict_Clear` |
| dcopy | cypy | cpdef | public | `PyDict_Copy` |
| dnext | cypy | cdef | cimport | `PyDict_Next`; borrowed ptrs |
| dkeys | cypy | cdef | cimport | `PyDict_Keys` — slower than `list(d.keys())` |
| dvalues | cypy | cdef | cimport | `PyDict_Values` |
| ditems | cypy | cdef | cimport | `PyDict_Items` |
| dset_string | cypy | cdef | cimport | `PyDict_SetItemString` |
| ddel_string | cypy | cdef | cimport | `PyDict_DelItemString` |
| dget_string | cypy | cdef | cimport | `PyDict_GetItemString` |
| dget_string_ref | cypy | cdef | cimport | `PyDict_GetItemStringRef` |
| dcontains_string | cypy | cdef | cimport | `PyDict_ContainsString` |
| dpop_string | cypy | cdef | cimport | `PyDict_PopString` |
| PyDict_Check / Exact | C-API | used-by | — | → checks |
| PyDict_New / Proxy_New | C-API | used-by | — | → `dnew` / `dproxy` |
| PyDict_GetItem* / SetDefault* | C-API | used-by | — | → get / setdefault family |
| PyDict_Update / Merge / MergeFromSeq2 | C-API | used-by | — | → update/merge aliases |
| PyDict_Keys / Values / Items | C-API | used-by | — | → cdef only |
| PyDict_*String* / PopString / ContainsString | C-API | used-by | — | → cdef string-key aliases |
| PyDict_Watch / AddWatcher / Unwatch / ClearWatcher | C-API | tried | — | event hooks; not wrapped |
| `_PyDict_*` private | C-API | tried | — | KnownHash / LockHeld / etc.; not wrapped |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| dget | APPROVED | primary hit **0.66x** |
| dget_ref | APPROVED | **0.59x**; strong ref; status≠visible from Python alone |
| dget_with_error | APPROVED | **0.61x**; propagates hash/eq errors |
| dcontains | APPROVED | hit **0.69x** |
| dlen | APPROVED | **0.60x**; Cython typed `dict` rejects subtypes |
| deq / dict_eq | APPROVED | identity/size + richcompare (issue #20) |
| dsize | APPROVED | **0.58x**; use for subtypes / untyped |
| dcheck / dcheck_exact | APPROVED | **0.51x** / **0.54x** |
| dnew | APPROVED | **0.84x** vs `{}` |
| dproxy | APPROVED | **0.59x** vs `MappingProxyType` |
| dset | APPROVED | **1.01x** tie — API-clarity keep |
| ddel | APPROVED | **0.96x** — API-clarity keep (≤1.02) |
| dpop | APPROVED | **0.90x**; fixed new-ref ownership |
| dupdate | APPROVED | **0.81x** (`PyDict_Update`) |
| dmerge | APPROVED | **0.81x**; cheap Merge alias with override |
| dmerge_from_seq2 | APPROVED | **0.80x** |
| dsetdefault / dsetdefault_ref | APPROVED | **0.91x** each |
| dclear / dcopy | APPROVED | **0.91x** / **0.85x** |
| dnext | APPROVED (cimport) | borrowed iteration; no Python baseline |
| dkeys / dvalues / ditems | APPROVED (cimport) | ad-hoc: lose to `list(d.keys())` (~1.36x); not public |
| dset_string / ddel_string / dget_string* / dcontains_string / dpop_string | APPROVED (cimport) | C-string keys; temp unicode cost |
| PyDict_Watch* / `_PyDict_*` | REJECTED | watchers / private ABI — no wrap |

## Lifecycle

| Field | Value |
|-------|--------|
| Freeze | **1.0 Core** — public + documented cimport; see COVERAGE § 1.0 freeze |
| Iteration | 3 |
P26-07-22 — `*_eq` inventory Tier A (`cyeq_inventory_bench`)|
| Next action | — |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| dget | Faster than `dict.get` | `bench/cydict_bench.py` | hit **0.66x** | APPROVED | 3 |
| dget_ref | Strong-ref get wins | same | **0.59x** | APPROVED | 3 |
| dget_with_error | Error-aware get | same | **0.61x** | APPROVED | 3 |
| dcontains / dlen / dsize | Macro/C-API beat Python | same | 0.58–0.71x | APPROVED | 3 |
| dcheck* / dnew / dproxy | Type/ctor helpers | same | 0.51–0.84x | APPROVED | 3 |
| dset / ddel | Mutators | same | 1.01x / 0.96x | APPROVED (clarity) | 3 |
| dpop / dupdate / dmerge* / dsetdefault* / dclear / dcopy | Mutators | same | 0.80–0.91x | APPROVED | 3 |
| dkeys / ditems / dvalues | List materialize | ad-hoc timeit | ~1.36x vs `list(keys)` | APPROVED (cimport) | 3 |
| `*String*` / dnext | C-string / iterator | smoke + ABI | symbols present | APPROVED (cimport) | 3 |
| Watch / `_PyDict_*` | Rare / private | `nm` | exported but out of scope | REJECTED | 3 |

## Bench notes

- Harness: [`bench/cydict_bench.py`](../../bench/cydict_bench.py)
- Tier A baseline: plain Python dict methods / `MappingProxyType` / `isinstance`
- Primary: `dget` hit `key='symbol'`
- Gate: ratio ≤ 0.95 on primary (pass); mutator ties kept for API clarity
- Env: CPython 3.14.6 · Linux x86_64 · free-threaded (GIL off) · N=80000 RUNS=5

## Bench results

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| dget | hit | 1.27±0.07ms | 1.37ms | 0.66x | 0.69x | pass |
| dget | miss | 1.31±0.11ms | 1.44ms | 0.67x | 0.69x | pass |
| dget | stored None | 1.23±0.05ms | 1.28ms | 0.64x | 0.66x | pass |
| dget_ref | hit | 1.16±0.01ms | 1.16ms | 0.59x | 0.57x | pass |
| dget_ref | stored None | 1.17±0.02ms | 1.20ms | 0.61x | 0.60x | pass |
| dget_with_error | hit | 1.18±0.03ms | 1.22ms | 0.61x | 0.62x | pass |
| dcontains | hit | 1.15±0.01ms | 1.16ms | 0.69x | 0.69x | pass |
| dcontains | miss | 1.23±0.04ms | 1.30ms | 0.71x | 0.69x | pass |
| dlen | small | 0.98±0.03ms | 1.03ms | 0.60x | 0.62x | pass |
| dlen | n=256 | 0.93±0.03ms | 0.98ms | 0.58x | 0.60x | pass |
| dsize | small | 0.96±0.02ms | 0.98ms | 0.58x | 0.57x | pass |
| dcheck | dict | 0.89±0.02ms | 0.91ms | 0.51x | 0.51x | pass |
| dcheck_exact | exact | 0.89±0.02ms | 0.90ms | 0.54x | 0.54x | pass |
| dnew | empty | 1.46±0.07ms | 1.53ms | 0.84x | 0.86x | pass |
| dproxy | proxy | 1.73±0.04ms | 1.77ms | 0.59x | 0.57x | pass |
| dset | insert | 4.15±0.07ms | 4.22ms | 1.01x | 1.00x | tie / keep |
| ddel | delete | 4.53±0.05ms | 4.58ms | 0.96x | 0.95x | clarity keep |
| dpop | pop hit | 4.55±0.15ms | 4.80ms | 0.90x | 0.93x | pass |
| dupdate | update | 4.90±0.03ms | 4.95ms | 0.81x | 0.80x | pass |
| dmerge | merge override | 5.10±0.04ms | 5.17ms | 0.81x | 0.81x | pass |
| dmerge_from_seq2 | pairs | 5.33±0.10ms | 5.45ms | 0.80x | 0.81x | pass |
| dsetdefault | miss insert | 4.09±0.03ms | 4.12ms | 0.91x | 0.90x | pass |
| dsetdefault_ref | miss insert | 4.13±0.05ms | 4.18ms | 0.91x | 0.90x | pass |
| dclear | clear | 3.74±0.10ms | 3.87ms | 0.91x | 0.92x | pass |
| dcopy | small | 3.21±0.05ms | 3.27ms | 0.85x | 0.84x | pass |

Summary: 24/25 faster · 23/25 ≥5% gate · mean ratio **0.73x** · median **0.69x**.

## Experiment — `cydict-monkey` (archived)

Tried making **`d.pop(...)`** hit `PyDict_Pop` via C-level `ml_meth` swap. Pure-Python assign fails (immutable type).

**Not in prod.** Overview: [`docs/future/MONKEY.md`](../future/MONKEY.md). Recipe sources (private archive): [`archive/monkey-recipes`](https://github.com/ckirua/cypy-private/tree/archive/monkey-recipes/docs/future/monkey).

Snapshot: patched `d.pop` ≈ stock (~1.00x); explicit `dpop` ~1.06x vs stock. Kept as future/recreate-only.

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cydict.py`](../../bench/tier_b/cydict.py) · `cydict_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| dget | hit symbol | 7.03±0.19ms | 7.33ms | 6.13±0.04ms | **1.15x** | 1.18x | baseline faster |
| dcontains | hit | 5.72±0.01ms | 5.74ms | 5.73±0.04ms | **1.00x** | 0.99x | ~tie |
| dlen | n=3 | 3.00±0.11ms | 3.12ms | 2.91±0.01ms | **1.03x** | 1.06x | baseline faster |
| dcheck | dict | 2.49±0.01ms | 2.50ms | 2.49±0.00ms | **1.00x** | 1.00x | ~tie |

**Tier B takeaway:** primary `dget` **1.15x** vs `dict.get` — Cython emit slightly tighter; keep public (Tier A still wins vs Python).


### `*_eq` inventory (Tier A depth)

Harness: [`bench/cyeq_inventory_bench.py`](../../bench/cyeq_inventory_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| dict_eq | eq small | 1.95±0.11ms | 2.25ms | **0.78x** | 0.79x | APPROVED |
| dict_eq | ne small | 2.05±0.08ms | 2.26ms | **0.77x** | 0.77x | APPROVED |
| dict_eq | identity | 1.01±0.07ms | 1.14ms | **0.39x** | 0.41x | APPROVED |
### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| dict_eq | eq small | 23.76±0.85ms | 25.17ms | 23.10±0.19ms | **1.03x** | 1.08x | baseline faster |
| dict_eq | ne small | 26.73±0.03ms | 26.76ms | 26.31±0.06ms | **1.02x** | 1.01x | ~tie |
| dict_eq | identity | 2.51±0.00ms | 2.52ms | 22.96±0.09ms | **0.11x** | 0.11x | cypy faster |

**Tier B `*_eq` notes:**
- **`dict_eq`:** Identity **0.11x**; content eq/ne ~tie–slight lose vs Cython `dict == dict`. Keep for identity / API clarity.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. Identity **0.11x**; content eq/ne ~tie–slight lose vs Cython `dict == dict`. Keep for identity / API clarity.

**Tier B:** primary `dget` **1.15x** vs `dict.get` — Cython emit slightly tighter; keep public (Tier A still wins vs Python).

| Topic | Finding |
|-------|---------|
| Why `dget` wins | Skips `dict.get` method lookup / default-arg path; `PyDict_GetItem` borrowed lookup |
| Borrowed vs None | `GetItem` / public `dget`: missing **and** stored `None` both return `None` |
| Strong-ref status | `GetItemRef` status (0/1) distinguishes missing vs present-`None` **only in C**; Python wrappers still return `None` for both unless a status API is added |
| `dget_with_error` | Unhashable keys raise (`TypeError`); plain `GetItem` would suppress |
| `dpop` ownership | `PyDict_Pop` returns a **new** strong ref — must `Py_DECREF` after `<object>` cast (old wrap leaked / mismatched) |
| Exact `dict` typing | Cython `dict` params reject subtypes (`TypeError`); use `dsize` / `dcheck` for subclasses |
| `dlen` vs `dsize` | Same speed on exact dict; prefer `dlen` typed; `dsize` for `object` / subtypes |
| Views | `PyDict_Keys` etc. allocate lists and **lose** to `list(d.keys())` (~1.36x ad-hoc) and crush vs `.keys()` views → **cdef only** |
| C-string keys | `*String*` builds a temporary unicode per call — fine when the key is already `const char*` in Cython; prefer `str` objects on hot Python paths |
| `dupdate` / `dmerge` | Both aliased (`Update` ≡ `Merge(..., 1)`); `dmerge(..., override=False)` keeps existing keys |
| Watchers / `_PyDict_*` | Present on 3.14 `.so` but out of accelerator scope → REJECTED |

## Done when

- [x] Full inventory vs `cpython.dict` (+ Pop/ContainsString)
- [x] Try-all + **depth** (None/borrowed, subtypes, views, string keys, ownership)
- [x] Bench results + experiment conclusions in **this** file
- [x] Before merge: `.pyi` one-liners; lean `.pxd`; views/string/`dnext` not public
