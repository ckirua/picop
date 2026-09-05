# cymodule

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.module` |
| Sources | `src/cypy/cymodule.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Module checks, construction, import helpers. Prefer `AddObjectRef` over stealing `AddObject`.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| mod_check* / new* / get_name/filename / add_*_ref / import* / magic | public | |
| mod_eq / modeq | public | identity eq (`object.__eq__`); soft `modeq`; not `hot` |
| get_dict / add_object (steal) / get_state / add_module / modules_dict | cimport | |
| ExtendInittab / ImportFrozen / ExecCode* | — | REJECTED (process-init / niche) |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| check / get_name / import / magic | APPROVED | **0.22–0.79x** |
| mod_eq / modeq | APPROVED | identity equality (issue #40); not `hot` |
| mod_new_object | APPROVED (API) | **0.99x** |
| get_dict / steal add / state | APPROVED (cimport) | borrowed / steal / void* |
| ExtendInittab / Frozen / ExecCode | REJECTED | pre-init / niche |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-07-22 — Tier B `*_eq` inventory|
| Next action | — |

## Decision log

| Function | Result | Decision | Iteration |
|----------|--------|----------|-----------|
| checks/import/magic | 0.22–0.79x | APPROVED | 1 |
| mod_eq / modeq | identity | APPROVED | 1 |
| AddObject | steals ref | APPROVED (cimport) | 1 |
| AddObjectRef | safe alias | APPROVED | 1 |

## Bench notes

- Harness: [`bench/cymodule_bench.py`](../../bench/cymodule_bench.py) · N=80000

## Bench results

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| mod_check | math / int | 0.46x / 0.39x | pass |
| mod_check_exact | math | 0.48x | pass |
| mod_get_name | | 0.79x | pass |
| mod_new_object | | 0.99x | API |
| mod_import | math | 0.49x | pass |
| mod_magic_number | | 0.22x | pass |

Summary: 6/7 gate · mean **0.55x**.

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cymodule.py`](../../bench/tier_b/cymodule.py) · `cymodule_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| mod_check | sys | 3.06±0.07ms | 3.15ms | 6.71±0.11ms | **0.46x** | 0.46x | cypy faster |

**Tier B takeaway:** primary `mod_check` **0.46x** vs typed Cython baseline (sys).



### `mod_eq` (Tier A depth)

Harness: [`bench/cyeq_misc_bench.py`](../../bench/cyeq_misc_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| mod_eq | identity | 0.97±0.03ms | 1.03ms | **0.55x** | 0.56x | APPROVED |

### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| mod_eq | identity | 2.50±0.01ms | 2.51ms | 4.98±0.02ms | **0.50x** | 0.50x | cypy faster |

**Tier B `*_eq` notes:**
- **`mod_eq`:** **0.50x** win — identity.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. **0.50x** win — identity.

**Tier B:** `mod_check` **0.43x** vs ModuleType isinstance.

| Topic | Finding |
|-------|---------|
| Import win | C `ImportModule` vs importlib path |
| Magic win | Direct long vs bytes decode |
| AddObject | Steals — keep cdef; public uses AddObjectRef |
| Cheap alias | New + NewObject both wrapped |
| Why win | Module type check + dict/name getters avoid attribute machinery |
| Scale | Create ~tie with `ModuleType(name)`; GetDict wins vs `mod.__dict__` (~0.49x) |
| Safety | SetDoc/AddObject mutate module state — GIL / free-threading: serialize writers |
| ABI | Multi-phase init helpers stay for extension authors (cimport) |
| `mod_eq` | Identity (`a is b`) — CPython `object.__eq__`; soft `modeq`; measured; leave off `hot` (clarity / not a starter) |


## Done when

- [x] Try-all + depth + benches + `.pyi`
