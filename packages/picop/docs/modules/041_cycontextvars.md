# cycontextvars

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.contextvars` |
| Sources | `src/cypy/cycontextvars.pxd`, `.pyx`, `.pyi` |
| Surface | public |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

Context / ContextVar construction and checks for Cython.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| ctx_* / ctxvar_* / ctxtoken_check_exact | public | Get omitted (out-param API) |
| context_eq / ctxeq | public | `Context` value eq (issue #44); soft `ctxeq`; not `hot` |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| checks / copy_current / new | APPROVED/API | see benches |
| context_eq / ctxeq | APPROVED | Tier A **0.55–0.81x** vs `==` (issue #44); not `hot` |
| Get out-param | REJECTED as public | needs ``PyObject**``; use ContextVar.get in Python |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 3 |
| Last pass | 2026-07-22 — Tier B `*_eq` inventory|
| Next action | — |

## Bench notes

- Harness: [`bench/cycontextvars_bench.py`](../../bench/cycontextvars_bench.py)

## Bench results

Harness: [`bench/cycontextvars_bench.py`](../../bench/cycontextvars_bench.py) · tier A · CPython 3.14 · N=80_000

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| ctx_check | context | **0.52x** | APPROVED |
| ctxvar_check | ContextVar | **0.50x** | APPROVED |
| ctx_copy_current | — | **1.11x** | APPROVED (API) |
| ctx_new / ctxvar_new | — | **0.26x** | APPROVED |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cycontextvars.py`](../../bench/tier_b/cycontextvars.py) · `cycontextvars_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| ctx_check_exact | Context | 2.86±0.19ms | 3.13ms | 5.43±0.02ms | **0.53x** | 0.57x | cypy faster |

**Tier B takeaway:** primary `ctx_check_exact` **0.53x** vs typed Cython baseline (Context).



### `context_eq` (Tier A depth)

Harness: [`bench/cycontextvars_bench.py`](../../bench/cycontextvars_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| context_eq | eq empty | 1.20±0.11ms | 1.38ms | **0.70x** | 0.78x | APPROVED |
| context_eq | identity | 0.94±0.03ms | 0.99ms | **0.55x** | 0.56x | APPROVED |
| context_eq | eq filled | 2.57±0.05ms | 2.65ms | **0.81x** | 0.79x | APPROVED |
| context_eq | ne filled | 2.59±0.06ms | 2.70ms | **0.63x** | 0.42x | APPROVED |
| context_eq | ne filled/empty | 1.30±0.21ms | 1.83ms | **0.76x** | 1.01x | APPROVED |

### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| context_eq | eq values | 41.04±0.53ms | 41.80ms | 40.01±0.36ms | **1.03x** | 1.03x | baseline faster |
| context_eq | ne values | 41.17±0.50ms | 41.89ms | 40.45±0.60ms | **1.02x** | 1.02x | ~tie |
| context_eq | identity | 2.54±0.02ms | 2.57ms | 6.09±0.05ms | **0.42x** | 0.42x | cypy faster |

**Tier B `*_eq` notes:**
- **`context_eq`:** Identity **0.42x**; value eq/ne ~tie (**1.02–1.03x**).

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. Identity **0.42x**; value eq/ne ~tie (**1.02–1.03x**).

**Tier B:** `ctx_check_exact` **0.52x** vs `type is Context`.

| Topic | Finding |
|-------|---------|
| Why checks/new win | Type slots and C constructors beat `isinstance` / Python `Context()` paths |
| Why copy ~ties | Same C copy of current context; wrapper adds little vs `copy_context()` |
| ABI / ownership | `Get` uses `PyObject**` out-param — REJECTED as public; use `ContextVar.get` |
| GIL / safety | Context enter/exit mutate thread-local state under GIL — pair carefully in Cython |
| Prefer | Checks + New for Cython tooling; skip public Get out-param wrappers |
| `context_eq` | Identity + richcompare — same as ``Context.__eq__``. Tier A **0.55–0.81x** vs `==` (empty/filled/ne). Soft `ctxeq`. Prefer over `obj_eq` when both sides are known Contexts. Skip ContextVar/Token eqs → `obj_eq`. See [`EQ_RUNTIME.md`](../EQ_RUNTIME.md). |

## Done when

- [x] Try-all + depth + benches + `.pyi`
- [x] `context_eq` / `ctxeq` (issue #44) — public (not hot)

### Ops remaining inventory (Tier A)

Harnesses: [`bench/cyaccessors_inventory_bench.py`](../../bench/cyaccessors_inventory_bench.py) / [`bench/cyruntime_inventory_bench.py`](../../bench/cyruntime_inventory_bench.py). See [`OPS_INVENTORY.md`](../OPS_INVENTORY.md) + [`OPS_INVENTORY_TIERB.md`](../OPS_INVENTORY_TIERB.md) for status / Tier B n/a.
