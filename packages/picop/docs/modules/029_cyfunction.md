# cyfunction

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.function` |
| Sources | `src/cypy/cyfunction.pxd`, `.pyx`, `.pyi` |
| Surface | public |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Function-object checks and field accessors beat attribute lookup from Python.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| func_check / new / get_* / set_* | public | getters INCREF borrowed |
| func_eq / funceq | public | identity eq (`object.__eq__`); soft `funceq`; not `hot` |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| func_check / get_code / globals / defaults | APPROVED | **0.40–0.63x** |
| func_new / set_* | APPROVED (API) | construction / mutation completeness |
| func_eq / funceq | APPROVED | identity equality (issue #40); not `hot` |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-07-22 — Tier B `*_eq` inventory|
| Next action | — |

## Decision log

| Function | Result | Decision | Iteration |
|----------|--------|----------|-----------|
| check/getters | 0.40–0.63x | APPROVED | 1 |
| new/set | API | APPROVED (API) | 1 |
| func_eq / funceq | identity | APPROVED | 1 |

## Bench notes

- Harness: [`bench/cyfunction_bench.py`](../../bench/cyfunction_bench.py) · N=80000

## Bench results

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| func_check | func / builtin | 0.48x / 0.40x | pass |
| func_get_code | __code__ | 0.48x | pass |
| func_get_globals | | 0.63x | pass |
| func_get_defaults | | 0.49x | pass |

Summary: 5/5 gate · mean **0.49x**.

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cyfunction.py`](../../bench/tier_b/cyfunction.py) · `cyfunction_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| func_check | def | 2.93±0.17ms | 3.12ms | 8.05±0.06ms | **0.36x** | 0.38x | cypy faster |

**Tier B takeaway:** primary `func_check` **0.36x** vs typed Cython baseline (def).



### `func_eq` (Tier A depth)

Harness: [`bench/cyeq_misc_bench.py`](../../bench/cyeq_misc_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| func_eq | identity | 0.97±0.04ms | 1.06ms | **0.54x** | 0.56x | APPROVED |
| func_eq | ne | 0.97±0.02ms | 1.01ms | **0.54x** | 0.53x | APPROVED |

### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| func_eq | identity | 2.49±0.01ms | 2.50ms | 4.98±0.01ms | **0.50x** | 0.50x | cypy faster |
| func_eq | ne | 2.50±0.00ms | 2.51ms | 6.18±0.02ms | **0.41x** | 0.40x | cypy faster |

**Tier B `*_eq` notes:**
- **`func_eq`:** **0.41–0.50x** win — identity (`is`) vs Cython `==` on functions.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. **0.41–0.50x** win — identity (`is`) vs Cython `==` on functions.

**Tier B:** `func_check` **0.33x** vs FunctionType isinstance.

| Topic | Finding |
|-------|---------|
| Check win | Type slot vs isinstance(FunctionType) |
| Getter win | Direct C struct fields vs descriptor attr |
| Borrowed | Get* return borrowed — wrappers INCREF for safe owned Python refs |
| SetDefaults/Closure | SystemError on bad types — documented by C-API |
| `func_eq` | Identity (`a is b`) — CPython `object.__eq__`; soft `funceq`; measured; leave off `hot` (clarity / not a starter) |

## Done when

- [x] Try-all + depth + benches + `.pyi`
