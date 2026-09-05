# cymethod

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.method` |
| Sources | `src/cypy/cymethod.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Bound-method checks and field access. `PyMethod_New` is 2-arg on 3.14 (Cython Includes still show 3).

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| method_check / new | public | |
| method_eq / methodeq | public | richcompare eq (`method_richcompare`); soft `methodeq`; not `hot` |
| method_get_function / method_get_self | public | preferred spelling; checked `PyMethod_Function` / `Self` |
| method_function / method_self | cimport impl | 0.3: cdef-only; prefer `method_get_*` |
| method_function_unchecked / method_self_unchecked | cimport | unchecked `GET_*` macros (not identity with checked getters) |
| PyMethod_Class | — | REJECTED (ABI missing 3.14) |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| method_check / function / self / get_* | APPROVED | **0.41–0.52x** |
| method_eq / methodeq | APPROVED | content equality (issue #40); not `hot` |
| method_new | APPROVED (API) | **1.00x** ~tie |
| *_unchecked (GET_*) | APPROVED (cimport) | unchecked |
| Class | REJECTED | missing 3.14 |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-07-22 — Tier B `*_eq` inventory|
| Next action | — |

## Decision log

| Function | Result | Decision | Iteration |
|----------|--------|----------|-----------|
| check/getters | 0.41–0.52x | APPROVED | 1 |
| method_eq / methodeq | richcompare | APPROVED | 1 |
| new | 1.00x | APPROVED (API) | 1 |
| Class | missing | REJECTED | 1 |

## Bench notes

- Harness: [`bench/cymethod_bench.py`](../../bench/cymethod_bench.py) · N=80000

## Bench results

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| method_check | bound / function | 0.48x / 0.41x | pass |
| method_function / self | | 0.52x / 0.50x | pass |
| method_new | bind | 1.00x | API |

Summary: 4/5 gate · mean **0.58x**.

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cymethod.py`](../../bench/tier_b/cymethod.py) · `cymethod_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| method_check | bound | 3.04±0.08ms | 3.14ms | 6.88±0.07ms | **0.44x** | 0.45x | cypy faster |

**Tier B takeaway:** primary `method_check` **0.44x** vs typed Cython baseline (bound).



### `method_eq` (Tier A depth)

Harness: [`bench/cyeq_misc_bench.py`](../../bench/cyeq_misc_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| method_eq | same bound | 1.23±0.04ms | 1.31ms | **0.67x** | 0.68x | APPROVED |
| method_eq | diff self | 1.27±0.07ms | 1.40ms | **0.68x** | 0.72x | APPROVED |

### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| method_eq | same bound | 6.55±0.01ms | 6.56ms | 6.58±0.05ms | **1.00x** | 0.98x | ~tie |
| method_eq | diff self | 6.57±0.02ms | 6.60ms | 6.55±0.01ms | **1.00x** | 1.01x | ~tie |

**Tier B `*_eq` notes:**
- **`method_eq`:** ~tie (**1.00x**) — richcompare already tight in Cython.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. ~tie (**1.00x**) — richcompare already tight in Cython.

**Tier B:** `method_check` **0.43x** vs MethodType isinstance.

| Topic | Finding |
|-------|---------|
| New arity | 3.14 `PyMethod_New(func, self)` — no `cls` (Py2 unbound removed) |
| Class gone | No `PyMethod_Class` in headers |
| GET_* | Unchecked inlines — cdef |
| Cheap aliases | GET_FUNCTION/SELF wrapped alongside checked Function/Self |
| Why win | Direct C method object fields vs descriptor `__func__`/`__self__` |
| Scale | BindMethod ~tie with Python bind (1.04x) — API keep for Cython call sites |
| Safety | GetFunction/GetSelf return borrowed refs — wrappers own for Python return |
| Subtype | Check distinguishes builtin FunctionType vs bound method |
| `method_eq` | Bound-method richcompare; Tier A **0.67–0.68x** vs `==`. |


## Done when

- [x] Try-all + depth + benches + `.pyi`

### Stub visibility (2026-08-02)

- Stub-hidden (Tier A `>1.02x`): `method_new`. Still `cpdef`.

