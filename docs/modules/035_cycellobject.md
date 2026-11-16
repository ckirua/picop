# cycellobject

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.cellobject` |
| Sources | `src/picop/cycellobject.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Closure cell objects for Cython/function tooling.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| cell_check / new / get / set / swap / empty | public | swap performs one critical-section replacement; empty creates a genuinely empty cell |
| cell_eq / celleq | public | content eq (`cell_richcompare`); soft `celleq`; not `hot` |
| cell_get_unchecked / set_unchecked | cimport | GET/SET macros |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| cell_check / get / new / swap / empty | APPROVED | see benches; swap is single critical-section replacement |
| cell_set | APPROVED (API) | mutation |
| cell_eq / celleq | APPROVED | content equality (issue #37); not `hot` |
| GET/SET unchecked | APPROVED (cimport) | no checks / SET skips INCREF |
| cell_swap_unchecked | APPROVED (cimport) | only if Tier B demonstrates measurable benefit; omitted absent evidence |
| PyCell_GetRef / PyCell_SetTakeRef / PyCell_SwapTakeRef | REJECTED | internal/pycore_cell.h requires Py_BUILD_CORE; Cython has no take-ref/steal primitive, so stealing caller's reference leaves cell dangling |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
P26-07-22 — `*_eq` inventory Tier A (`cyeq_inventory_bench`)|
| Next action | — |

## Decision log

| Function | Decision | Iteration |
|----------|----------|-----------|
| public | APPROVED | 1 |
| cell_eq / celleq | APPROVED | 1 |
| macros | APPROVED (cimport) | 1 |
| `cell_get_unchecked` | APPROVED (cimport) — `PyCell_GET` is a borrowed macro, so it is declared `PyObject *` and promoted with an `<object>` cast; declaring it as `object` decref'd the target once per call | 2 |
| `cell_swap` | APPROVED | checked wrapper calls shim that takes one critical section and returns old contents as a new reference |
| `cell_empty` | APPROVED | `PyCell_New(NULL)` creates an actually empty cell; `cell_new(None)` contains None |

## Bench notes

- Harness: [`bench/cycellobject_bench.py`](../../bench/cycellobject_bench.py)

## Bench results

### Order 088 — swap and empty-cell decisions

| Candidate | Decision | Mechanism |
|-----------|----------|-----------|
| `cell_swap` | APPROVED | One critical section; incref replacement before cell ownership; old contents returned as new reference |
| `cell_empty` | APPROVED | `PyCell_New(NULL)` is semantically distinct from `cell_new(None)` |
| `cell_swap_unchecked` | REJECTED | No measured Tier B benefit to justify unchecked public cimport surface |
| `PyCell_GetRef` / `PyCell_SetTakeRef` / `PyCell_SwapTakeRef` | REJECTED | `internal/pycore_cell.h` is restricted to `Py_BUILD_CORE`; Cython 3.3.1 has no take-ref/steal primitive, and naive steal can leave a dangling cell pointer |

Harness: [`bench/cycellobject_bench.py`](../../bench/cycellobject_bench.py) · tier A · CPython 3.14 · N=80_000

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| cell_check | cell | **0.48x** | APPROVED |
| cell_check | miss | **0.40x** | APPROVED |
| cell_get | filled | **0.51x** | APPROVED |
| cell_new | empty | **0.94x** | APPROVED (API) |


### Order 088 measurements (N=80,000 × 5)

| Helper / comparison | CPython 3.14 | CPython 3.15 | Decision |
|---------------------|--------------|--------------|----------|
| `cell_swap` / get+set | **0.29x** | **0.30x** | APPROVED |
| `cell_empty` / `cell_new(None)` | **0.95x** | **0.94x** | APPROVED (API clarity); parity on speed, the value is the empty-vs-`None` semantics |

### Order 088 Tier B (N=2,000,000 × 5)

| Helper / typed baseline | CPython 3.14 | CPython 3.15 |
|-------------------------|--------------|--------------|
| `cell_swap` / `cell_get` + `cell_set` | **0.36x** | **0.31x** |

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| cell_check | cell, 3.14 | 2.73±0.02ms | 2.76ms | 92.16±3.84ms | **0.03x** | 0.03x | cypy faster |
| cell_check | cell, 3.15 | 2.71±0.01ms | 2.72ms | 90.45±1.76ms | **0.03x** | 0.03x | cypy faster |
| cell_swap | get+set, 3.14 | 5.45±0.07ms | 5.56ms | 15.11±0.29ms | **0.36x** | 0.36x | cypy faster |
| cell_swap | get+set, 3.15 | 5.49±0.10ms | 5.60ms | 17.74±1.64ms | **0.31x** | 0.27x | cypy faster |

**Tier B takeaway:** `cell_check` **0.03x** and `cell_swap` **0.36x / 0.31x** vs the typed Cython baseline.



### `*_eq` inventory (Tier A depth)

Harness: [`bench/cyeq_inventory_bench.py`](../../bench/cyeq_inventory_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| cell_eq | identity | 0.95±0.04ms | 1.00ms | **0.51x** | 0.50x | APPROVED |
| cell_eq | same value | 1.36±0.06ms | 1.46ms | **0.72x** | 0.72x | APPROVED |
| cell_eq | ne | 1.34±0.02ms | 1.37ms | **0.71x** | 0.68x | APPROVED |
### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| cell_eq | identity | 2.52±0.01ms | 2.53ms | 11.53±0.04ms | **0.22x** | 0.22x | cypy faster |
| cell_eq | same value | 10.20±0.18ms | 10.34ms | 11.15±0.02ms | **0.91x** | 0.92x | cypy faster |
| cell_eq | ne | 10.05±0.06ms | 10.14ms | 11.51±0.02ms | **0.87x** | 0.88x | cypy faster |

**Tier B `*_eq` notes:**
- **`cell_eq`:** Identity **0.22x**; same-value/ne **0.87–0.91x** — identity short-circuit + richcompare.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. Identity **0.22x**; same-value/ne **0.87–0.91x** — identity short-circuit + richcompare.

**Tier B:** `cell_check` **0.03x** vs the typed Cython baseline (3.14 and 3.15).

Order 088 depth probe: `cell_swap` replaced A with B and returned the identical A; `sys.getrefcount(A)` was **2 before**, **2 after the call**, and **1 after deleting the returned reference** (local-variable baseline included). The cell held B after the call; swapping a genuinely empty cell returned `None` and then stored B. This is balanced new-reference ownership: the shim increfs B before transferring it into the cell, while Cython owns the returned old reference. `cell_empty()` constructs with `PyCell_New(NULL)`, not `PyCell_New(Py_None)`, so `cell_get` raises for the former. Empty-cell access turned out to be a landmine: a C probe on CPython 3.14.7 shows `PyCell_Get` returns NULL **without setting an exception**, so an `object`-typed Cython extern raises with no exception object and segfaults inside the traceback machinery; `cell_get` now reads the borrowed `PyCell_GET` pointer under a critical section and raises `ValueError("cell is empty")` itself. The internal GetRef/SetTakeRef/SwapTakeRef route stays rejected: `internal/pycore_cell.h` errors outside `Py_BUILD_CORE`, and Cython 3.3.1 provides no take-ref/steal primitive; a naive stolen temporary can leave a dangling cell pointer. Swap wins over the typed get/set pair at both ABIs (Tier A **0.30x/0.28x**, Tier B **0.36x/0.31x**), demonstrating a robust crossover without sacrificing correct refcount behavior. The critical-section sequence is ABI-compatible with the public cell layout and avoids the two separate critical sections in get+set.

| Topic | Finding |
|-------|---------|
| Why check/get win | Slot check and `PyCell_Get` beat `CellType`/`cell_contents` attribute paths |
| Ownership / refcount | Public `cell_set` adjusts refs; `PyCell_SET` skips INCREF — cimport only |
| ABI / safety | Unchecked GET/SET macros assume a live cell; wrong type → undefined |
| Scale | Cell ops are O(1); no size crossover — cost is wrapper vs attribute |
| New(None) | Empty cell allowed; construction ~ties Python `types.CellType` |
| `cell_eq` | Content equality via richcompare (not identity); empty↔empty True; soft `celleq`; measured; leave off `hot` (clarity / not a starter) |

## Done when

- [x] Try-all + depth + benches + `.pyi`
