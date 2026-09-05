# cyobject

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.object` |
| Sources | `src/cypy/cyobject.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Abstract object protocol for Cython call sites. From Python, builtins usually win; keep as API bridge + cimport for typed code.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| attr / call / truth / len / item / type helpers | public (cpdef) | Tier A losers stub-hidden from `.pyi` (still importable) |
| obj_eq / oeq | public | RichCompareBool(EQ); soft `oeq`; on `protocols`, not `hot` |
| obj_size | public (cpdef) | Length alias; stub-hidden with `obj_len` |
| typecheck / TYPE / Generic* / Malloc* | cimport | |
| Cmp / Compare | — | REJECTED (ABI missing) |
| CallFunction* varargs | — | REJECTED (unwrappable varargs; use Call) |
| Print | — | REJECTED (FILE*; no public need) |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| obj_richcompare_bool | APPROVED | **0.71x** |
| obj_eq / oeq | APPROVED | thin EQ wrap of richcompare_bool (issue #35); on `protocols`, not `hot` |
| most public helpers | APPROVED (API) | **0.98–1.23x** — Cython bridge; stub-hidden when Tier A `> 1.02x` |
| stub visibility | equality family | `.pyi` keeps `obj_richcompare*` / `obj_eq` (+ unmeasured mutators); losers omitted |
| typecheck / malloc / generic | APPROVED (cimport) | pointers / allocator |
| Cmp / Compare | REJECTED | missing 3.14 |
| CallFunction/Method varargs | REJECTED | use `obj_call` |
| Print | REJECTED | FILE* surface |

## Lifecycle

| Field | Value |
|-------|--------|
| Freeze | **Provisional (Protocols)** after 1.0 — not Core; may evolve under minors |
| Iteration | 1 |
| Last pass | 2026-08-02 — stub-hide Tier A `>1.02x` from `.pyi` |
| Next action | — |

## Decision log

| Function | Result | Decision | Iteration |
|----------|--------|----------|-----------|
| richcompare_bool | 0.71x | APPROVED | 1 |
| obj_eq / oeq | thin EQ wrap; identity short-circuit (nan is nan → True) | APPROVED | 1 |
| hasattr/getattr/len/… | 1.03–1.23x | APPROVED (API) | 1 |
| Cmp/Compare | ctypes missing | REJECTED | 1 |

## Bench notes

- Harness: [`bench/cyobject_bench.py`](../../bench/cyobject_bench.py) · N=80000

## Bench results

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| obj_richcompare_bool | 1==1 | 0.71x | pass |
| obj_str | 42 | 0.98x | ~tie API |
| hasattr / getattr / type / … | | 1.03–1.23x | API |
| obj_len / size | dict | 1.10–1.12x | API |

Summary: 1/15 gate · mean **1.08x**.

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cyobject.py`](../../bench/tier_b/cyobject.py) · `cyobject_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| obj_type | str | 2.94±0.04ms | 3.01ms | 2.81±0.14ms | **1.05x** | 1.02x | baseline faster |
| obj_len | tuple | 2.69±0.12ms | 2.88ms | 2.53±0.21ms | **1.06x** | 1.08x | baseline faster |

**Tier B takeaway:** primary `obj_type` **1.05x** vs typed Cython baseline (str).



### `obj_eq` (Tier A depth)

Harness: [`bench/cyeq_misc_bench.py`](../../bench/cyeq_misc_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| obj_eq | int eq | 1.03±0.08ms | 1.20ms | **0.67x** | 0.78x | APPROVED |
| obj_eq | nan is nan | 1.19±0.03ms | 1.25ms | **0.76x** | 0.75x | APPROVED |

### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| obj_eq | int eq | 3.05±0.02ms | 3.09ms | 5.79±0.05ms | **0.53x** | 0.53x | cypy faster |
| obj_eq | nan is nan | 4.89±0.01ms | 4.91ms | 5.02±0.04ms | **0.97x** | 0.96x | cypy faster |

**Tier B `*_eq` notes:**
- **`obj_eq`:** Int eq **0.53x**; nan **0.97x** (~tie) — generic richcompare EQ.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. Int eq **0.53x**; nan **0.97x** (~tie) — generic richcompare EQ.

**Tier B:** `obj_type`/`obj_len` ~**1.03–1.05x** — thin wrapper parity.

| Topic | Finding |
|-------|---------|
| Why lose | Python builtins specialize; abstract C-API adds wrapper frame from `cpdef` |
| Why richcompare wins | Avoids Python `==` bytecode / richcmp indirection in this microbench |
| Prefer typed | Use container modules when type known |
| Cheap alias | `obj_size` ≡ `obj_len` |
| `obj_eq` | Richcompare EQ + identity short-circuit; Tier A **0.67–0.76x**. |
| ABI | `PyObject_Cmp`/`Compare` gone; `Py_SIZE` is macro (not ctypes export) |
| Malloc | Process heap via Python allocator — cdef only |

## Done when

- [x] Try-all + depth + benches + `.pyi`

### Ops remaining inventory (Tier A)

Harnesses: [`bench/cyaccessors_inventory_bench.py`](../../bench/cyaccessors_inventory_bench.py) / [`bench/cyruntime_inventory_bench.py`](../../bench/cyruntime_inventory_bench.py). See [`OPS_INVENTORY.md`](../OPS_INVENTORY.md) + [`OPS_INVENTORY_TIERB.md`](../OPS_INVENTORY_TIERB.md) for status / Tier B n/a.
