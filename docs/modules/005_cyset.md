# cyset

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.set` (`Cython/Includes/cpython/set.pxd`) + `setobject.h` macros |
| Sources | `src/cypy/cyset.pxd`, `cyset.pyx`, `cyset.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Hot-path contains/len/checks/constructors for typed `set` / any-set, plus full include try-all (frozenset constructors + check macros). Mutators mirror `PySet_*` for Cython call sites; tier A from Python is often ~tie/lose to method bytecode.

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| scheck | cypy | cpdef | public | `PySet_Check` |
| scheck_exact | cypy | cpdef | public | `PySet_CheckExact` (header macro) |
| sany_check | cypy | cpdef | public | `PyAnySet_Check` |
| sany_check_exact | cypy | cpdef | public | `PyAnySet_CheckExact` |
| sfrozen_check | cypy | cpdef | public | `PyFrozenSet_Check` |
| sfrozen_check_exact | cypy | cpdef | public | `PyFrozenSet_CheckExact` |
| sempty | cypy | cpdef | public | `PySet_New(NULL)` |
| snew | cypy | cpdef | public | `PySet_New(iterable)` |
| sfrozen_empty | cypy | cpdef | public | `PyFrozenSet_New(NULL)` |
| sfrozen_new | cypy | cpdef | public | `PyFrozenSet_New(iterable)` |
| slen | cypy | cpdef | public | `PySet_GET_SIZE` — exact `set` |
| seteq | cypy | cpdef | public | identity/size + richcompare; preferred `set_eq` (not soft `seq`) |
| fseteq | cypy | cpdef | public | identity/size + richcompare; preferred `frozenset_eq` |
| ssize | cypy | cpdef | public | `PySet_Size` — set/frozenset/subtypes |
| scontains | cypy | cpdef | public | `PySet_Contains` (any-set) |
| sadd | cypy | cpdef | public | `PySet_Add` |
| sdiscard | cypy | cpdef | public | `PySet_Discard` — no `PySet_Remove` |
| spop | cypy | cpdef | public | `PySet_Pop` — raises `KeyError` if empty |
| sclear | cypy | cpdef | public | `PySet_Clear` |
| scopy | cypy | cpdef | public | `PySet_New(s)` copy |
| supdate | cypy | cpdef | public | `_PySet_Update` (exported internal) |
| PySet_* / PyFrozenSet_* / PyAnySet_* | C-API | used-by | — | all include + CheckExact macros |
| `_PySet_AddTakeRef` / `Contains` / `NextEntry*` / `Dummy` | C-API | tried | — | private; not wrapped |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| scontains | APPROVED | primary hit **0.71x**; frozenset **0.73x** |
| slen / ssize | APPROVED | **0.61x** / **0.63–0.64x** |
| seteq / set_eq | APPROVED | identity/size + richcompare (issue #21) |
| fseteq / frozenset_eq | APPROVED | identity/size + richcompare (issue #22) |
| scheck / exact | APPROVED | **0.52x** / **0.57x** |
| sany_* / sfrozen_* | APPROVED | **0.29–0.58x** vs `isinstance` |
| sempty / snew / sfrozen_* / scopy | APPROVED | **0.72–0.93x** |
| sadd | APPROVED | **1.01x** tie — API-clarity |
| sclear | APPROVED | **1.03x** — API-clarity C-API mirror |
| sdiscard / spop / supdate | APPROVED | **1.06–1.13x** — keep as C-API mirrors (Python method wins on tier A call overhead) |
| `_PySet_*` (except Update) | REJECTED | private |
| `PySet_Remove` | REJECTED | no such ABI — use `sdiscard` |

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
| scontains | Beat `in` | `bench/cyset_bench.py` | **0.71x** hit | APPROVED | 1 |
| slen / ssize / checks / ctors | Macro/C-API | same | 0.29–0.93x | APPROVED | 1 |
| sadd | Thin Add | same | **1.01x** | APPROVED (clarity) | 1 |
| sdiscard / spop / sclear / supdate | Thin mutators | same | 1.03–1.13x | APPROVED (clarity / Cython entry) | 1 |
| private `_PySet_*` | — | nm | exported but private | REJECTED | 1 |

## Bench notes

- Harness: [`bench/cyset_bench.py`](../../bench/cyset_bench.py)
- Primary: `scontains` hit on small set
- Env: CPython 3.14.6 · Linux x86_64 · GIL on (venv bench) · N=80000 RUNS=5

## Bench results

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| scontains | hit small | 1.15±0.03ms | 1.20ms | 0.71x | 0.73x | pass |
| scontains | miss small | 2.30±0.13ms | 2.50ms | 0.81x | 0.84x | pass |
| scontains | hit n=64 | 1.10±0.01ms | 1.11ms | 0.69x | 0.67x | pass |
| scontains | miss n=64 | 1.15±0.02ms | 1.17ms | 0.71x | 0.70x | pass |
| scontains | frozenset hit | 1.20±0.06ms | 1.30ms | 0.73x | 0.76x | pass |
| slen | small | 0.97±0.06ms | 1.07ms | 0.61x | 0.66x | pass |
| slen | n=64 | 0.96±0.06ms | 1.04ms | 0.45x | 0.26x | pass |
| ssize | set | 1.02±0.02ms | 1.05ms | 0.63x | 0.61x | pass |
| ssize | frozenset | 1.03±0.08ms | 1.16ms | 0.64x | 0.70x | pass |
| scheck | set | 0.89±0.05ms | 0.97ms | 0.52x | 0.53x | pass |
| scheck_exact | exact | 0.92±0.05ms | 1.00ms | 0.57x | 0.61x | pass |
| sany_check | frozenset | 0.89±0.01ms | 0.90ms | 0.29x | 0.29x | pass |
| sany_check_exact | exact | 0.89±0.04ms | 0.96ms | 0.42x | 0.43x | pass |
| sfrozen_check | frozenset | 0.92±0.03ms | 0.95ms | 0.52x | 0.52x | pass |
| sfrozen_check_exact | exact | 0.93±0.08ms | 1.05ms | 0.58x | 0.62x | pass |
| sempty | empty | 1.80±0.06ms | 1.86ms | 0.72x | 0.70x | pass |
| sfrozen_empty | empty | 1.78±0.02ms | 1.80ms | 0.76x | 0.75x | pass |
| snew | list3 | 2.91±0.03ms | 2.93ms | 0.77x | 0.74x | pass |
| sfrozen_new | list3 | 2.88±0.02ms | 2.92ms | 0.79x | 0.78x | pass |
| scopy | small | 2.05±0.01ms | 2.07ms | 0.73x | 0.73x | pass |
| scopy | n=64 | 11.08±0.08ms | 11.20ms | 0.93x | 0.94x | pass |
| sadd | add | 3.51±0.12ms | 3.70ms | 1.01x | 1.05x | tie (clarity) |
| sdiscard | hit | 3.59±0.06ms | 3.67ms | 1.08x | 1.09x | clarity keep |
| sdiscard | miss | 3.52±0.07ms | 3.64ms | 1.06x | 1.05x | clarity keep |
| spop | n=3 | 3.26±0.06ms | 3.36ms | 1.13x | 1.15x | clarity keep |
| sclear | n=3 | 4.42±0.01ms | 4.43ms | 1.03x | 1.00x | clarity keep |
| supdate | list3 | 4.55±0.08ms | 4.63ms | 1.07x | 1.07x | clarity keep |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cyset.py`](../../bench/tier_b/cyset.py) · `cyset_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| scontains | hit | 3.82±0.00ms | 3.82ms | 4.19±0.01ms | **0.91x** | 0.91x | cypy faster |
| slen | n=4 | 3.01±0.20ms | 3.22ms | 2.85±0.20ms | **1.06x** | 1.03x | baseline faster |
| scheck | set | 2.85±0.12ms | 3.04ms | 2.87±0.12ms | **0.99x** | 1.00x | ~tie |

**Tier B takeaway:** primary `scontains` **0.91x** vs typed `in` — small edge vs Cython emit.


### `*_eq` inventory (Tier A depth)

Harness: [`bench/cyeq_inventory_bench.py`](../../bench/cyeq_inventory_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| set_eq | eq small | 2.01±0.07ms | 2.20ms | **0.80x** | 0.83x | APPROVED |
| set_eq | ne small | 1.90±0.06ms | 2.05ms | **0.79x** | 0.76x | APPROVED |
| frozenset_eq | eq | 2.04±0.07ms | 2.11ms | **0.79x** | 0.76x | APPROVED |
| frozenset_eq | ne | 1.87±0.03ms | 1.91ms | **0.78x** | 0.77x | APPROVED |
### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| set_eq | eq small | 28.26±0.02ms | 28.29ms | 28.16±0.04ms | **1.00x** | 1.00x | ~tie |
| set_eq | ne small | 24.04±0.09ms | 24.12ms | 23.80±0.13ms | **1.01x** | 1.01x | ~tie |
| frozenset_eq | eq | 28.80±0.33ms | 29.15ms | 28.80±0.33ms | **1.00x** | 1.00x | ~tie |
| frozenset_eq | ne | 24.10±0.18ms | 24.31ms | 24.06±0.20ms | **1.00x** | 1.00x | ~tie |

**Tier B `*_eq` notes:**
- **`set_eq`:** ~tie (**1.00–1.01x**) vs typed Cython `set == set` — helper is thin richcompare wrapper.
- **`frozenset_eq`:** ~tie (**1.00x**) vs typed Cython `frozenset == frozenset`.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. ~tie (**1.00–1.01x**) vs typed Cython `set == set` — helper is thin richcompare wrapper.

**Tier B:** primary `scontains` **0.91x** vs typed `in` — small edge vs Cython emit.

- **Why win (contains/len/checks):** `PySet_Contains` / `GET_SIZE` / check macros avoid Python attribute/`isinstance` dispatch; primary hit **0.71x**, any-set checks vs `(set, frozenset)` tuple **0.29x**.
- **Scale:** hit/miss and n=4 vs n=64 — contains stays ~0.69–0.81x; `scopy` n=64 still **0.93x** (copy cost dominates).
- **Frozenset:** `scontains` / `ssize` accept any-set; constructors `sfrozen_empty` / `sfrozen_new` win **0.76–0.79x**.
- **Mutators lose from Python:** fresh-set benches are dominated by allocation; `set.add`/`discard`/`pop`/`update` bytecode beats an extra `cpdef` call (**1.01–1.13x**). Still APPROVED as C-API mirrors for Cython call sites (inline/`cdef` path), not as Python speedups.
- **`spop` safety:** removed prior `noexcept`→`None` swallow; empty set now raises **`KeyError`** like `set.pop()` / `PySet_Pop`.
- **No `PySet_Remove`:** ABI has only `Discard` (0/1/-1). No sibling alias to add.
- **`supdate`:** uses exported `_PySet_Update` (not in public `Python.h` on 3.14 — declared via a local prototype in `cyset.pxd`); same path as `set.update()`. Free-threaded: set mutators still need the usual object lock / critical section discipline as plain `set` methods.
- **Private rejects:** `_PySet_AddTakeRef`, `_PySet_Contains`, `_PySet_NextEntry*`, `_PySet_Dummy` — not wrapped.

## Done when

- [x] Full inventory vs mapped include (or declared custom surface)
- [x] Every row has workflow status
- [x] Lifecycle + next action filled
- [x] APPROVED / APPROVED (cimport) rows have decision-log evidence
- [x] REJECTED rows have policy or measured why
- [x] Present measuring: try-all **and** depth checklist in **this tracker’s** Experiment conclusions (**no skip**)
- [x] **Bench results** table filled in **this file** (not only PR)
- [x] **Before merge:** public PEP 257 one-liners in `cyset.pyi`; `.pxd` lean — [`PIPELINE.md`](../PIPELINE.md)

### Stub visibility (2026-08-02)

- Stub-hidden (Tier A `>1.02x`): `set_pop`. Still `cpdef`.

