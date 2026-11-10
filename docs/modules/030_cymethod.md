# cymethod

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.method` |
| Sources | `src/picop/cymethod.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Bound-method checks and field access. `PyMethod_New` is 2-arg on 3.14 (Cython Includes still show 3).

## Inventory

Full `cpython/method` / C-function surface, including the unchecked macros kept cimport-only.

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| `PyMethod_Check` | C-API | macro | `method_check` | bound Python methods only |
| `PyMethod_New` | C-API | function | `method_new` | 2-arg on 3.14+ (no `cls`) |
| `PyMethod_Function` / `PyMethod_Self` | C-API | function | `method_get_function` / `method_get_self` | checked, borrowed → owned |
| `PyMethod_GET_FUNCTION` / `GET_SELF` | C-API | macro | cimport-only `*_unchecked` | unchecked field reads |
| `PyMethod_Class` | C-API | — | — | REJECTED (ABI missing on 3.14) |
| `PyCFunction_Check` / `PyCFunction_CheckExact` | C-API | macro | `cfunction_check` / `cfunction_check_exact` | `PyCMethod` passes `PyCFunction_Check` (it is a subtype) |
| `PyCMethod_Check` / `PyCMethod_CheckExact` | C-API | macro | `cmethod_check` / `cmethod_check_exact` | C function carrying its defining class |
| `PyCFunction_GetSelf` | C-API | function | `cfunction_get_self` | `None` for static/plain builtins; `SystemError` on a non-C-function |
| `PyCFunction_GET_FUNCTION` / `GET_SELF` / `GET_FLAGS` / `GET_CLASS` | C-API | macro | cimport-only `*_unchecked` | `GET_FUNCTION` yields a raw C pointer, never a Python object |
| `PyClassMethod_New` / `PyStaticMethod_New` | C-API | function | `classmethod_new` / `staticmethod_new` | the descriptors `classmethod` / `staticmethod` build |
| `method_eq` / `methodeq` | cypy | helper | public / soft alias | richcompare equality (`__func__` + `__self__`), not identity |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| method_check / function / self / get_* | APPROVED | **0.41–0.52x** |
| method_eq / methodeq | APPROVED | content equality (issue #40); not `hot` |
| method_new | APPROVED (API) | **1.00x** ~tie |
| *_unchecked (GET_*) | APPROVED (cimport) | unchecked |
| Class | REJECTED | missing 3.14 |
| cfunction_check / cfunction_check_exact | APPROVED | Tier A **0.39–0.46x**, Tier B **0.11–0.16x** |
| cmethod_check / cmethod_check_exact | APPROVED (API) | type predicate with no plain-Python baseline; Tier A `n/a` |
| cfunction_get_self | APPROVED | Tier A **0.56x**, Tier B **0.30–0.45x** |
| classmethod_new / staticmethod_new | APPROVED | Tier A **0.20–0.21x**, Tier B **0.09x** |
| `PyCFunction_GET_FUNCTION` | REJECTED (as a public getter) | hands out a raw C entry point, not an object; unusable from Python |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 2 |
| Last pass | 2026-11-10 — Order 067: `cfunction_check` / `cfunction_check_exact`, `cmethod_check` / `cmethod_check_exact`, `cfunction_get_self`, `classmethod_new`, `staticmethod_new`; Tier A try-all + Tier B |
| Next action | — |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| check/getters | 0.41–0.52x | Tier A | pass | APPROVED | 1 |
| method_eq / methodeq | richcompare | Tier A + Tier B | 0.67–0.68x / ~1.00x | APPROVED | 1 |
| new | 1.00x | Tier A | tie | APPROVED (API) | 1 |
| Class | missing | ABI probe | not present in 3.14 headers | REJECTED | 1 |
| `cfunction_check` / `_exact` | C-callable detection needs a checked predicate, not `isinstance` | Tier A + Tier B | 0.39–0.46x / 0.11–0.16x | APPROVED | 2 |
| `cmethod_check` / `_exact` | `PyCMethod` is distinct from `PyCFunction` | type probe | `len` is exact `PyCFunction`; a slot-backed method is `PyCMethod` | APPROVED (API) | 2 |
| `cfunction_get_self` | static builtins have no self; class-bound C functions do | Tier A + Tier B | 0.56x / 0.30–0.45x | APPROVED | 2 |
| `classmethod_new` / `staticmethod_new` | descriptor construction from Cython should not go through the Python builtins | Tier A + Tier B | 0.20–0.21x / 0.09x | APPROVED | 2 |
| `PyCFunction_GET_FUNCTION` | exposing the entry point could help dispatch | ABI review | raw `void *`, never a Python object | REJECTED | 2 |

## Bench notes

- Harness: [`bench/cymethod_bench.py`](../../bench/cymethod_bench.py) · N=80000

## Bench results

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| method_check | bound / function | 0.48x / 0.41x | pass |
| method_function / self | | 0.52x / 0.50x | pass |
| method_new | bind | 1.00x | API |

Summary: 4/5 gate · mean **0.58x**.

### Order 067 pass (Tier A try-all)

Harness: [`bench/cymethod_bench.py`](../../bench/cymethod_bench.py) · CPython 3.14 · Linux x86_64 · GIL build · `N=80_000` × `runs=5`

| operation | case | picop mean±σ | p99 | baseline mean±σ | p99 | ratio | p99× | verdict |
|---|---|---:|---:|---:|---:|---:|---:|---|
| method_check | bound | 2.29±0.07ms | 2.40ms | 5.23±0.05ms | 5.31ms | **0.44x** | 0.45x | pass |
| method_check | function | 2.42±0.05ms | 2.47ms | 6.73±0.86ms | 8.19ms | **0.36x** | 0.30x | pass |
| method_get_function | `__func__` | 2.87±0.01ms | 2.89ms | 4.61±0.01ms | 4.62ms | **0.62x** | 0.63x | pass |
| method_get_self | `__self__` | 2.58±0.03ms | 2.64ms | 4.56±0.07ms | 4.64ms | **0.57x** | 0.57x | pass |
| method_new | bind | 3.73±0.07ms | 3.80ms | 3.66±0.06ms | 3.75ms | **1.02x** | 1.01x | API keep |
| cfunction_check | builtin | 2.28±0.04ms | 2.34ms | 5.06±0.08ms | 5.14ms | **0.45x** | 0.46x | pass |
| cfunction_check | bound method | 2.61±0.04ms | 2.65ms | 6.74±0.11ms | 6.87ms | **0.39x** | 0.39x | pass |
| cfunction_check_exact | builtin | 2.39±0.12ms | 2.59ms | 5.16±1.05ms | 6.95ms | **0.46x** | 0.37x | pass |
| cfunction_get_self | builtins module | 2.62±0.03ms | 2.65ms | 4.68±0.04ms | 4.74ms | **0.56x** | 0.56x | pass |
| classmethod_new | wrap | 4.47±0.09ms | 4.63ms | 21.92±0.35ms | 22.28ms | **0.20x** | 0.21x | pass |
| staticmethod_new | wrap | 4.59±0.00ms | 4.59ms | 21.51±0.27ms | 21.95ms | **0.21x** | 0.21x | pass |
| cmethod_check / cmethod_check_exact | — | — | — | — | — | n/a | — | no plain-Python baseline |

Summary: 11 measured operations, 10 picop faster · mean **0.48x** · median 0.45x (`method_new` 1.02x is the documented API keep).

### Order 067 pass (Tier B)

Harness: [`bench/tier_b/cymethod.py`](../../bench/tier_b/cymethod.py) · `cymethod_tb.pyx` · `CPY_TIERB_N=2_000_000` × `runs=5`

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| method_check | bound | 2.71±0.03ms | 2.74ms | 23.18±0.37ms | **0.12x** | 0.12x | cypy faster |
| cfunction_check | builtin | 3.01±0.05ms | 3.09ms | 27.67±6.86ms | **0.11x** | 0.08x | cypy faster |
| cfunction_check_exact | builtin | 2.99±0.78ms | 4.32ms | 18.70±4.16ms | **0.16x** | 0.18x | cypy faster |
| cfunction_get_self | builtin | 12.86±6.89ms | 24.58ms | 28.54±0.13ms | **0.45x** | 0.86x | cypy faster |
| cfunction_get_self | builtin (unchecked macro) | 8.49±0.06ms | 8.59ms | 28.55±0.28ms | **0.30x** | 0.30x | macro baseline |
| classmethod_new | wrap | 48.74±0.32ms | 49.18ms | 533.05±4.35ms | **0.09x** | 0.09x | cypy faster |
| staticmethod_new | wrap | 48.92±0.21ms | 49.20ms | 546.21±20.08ms | **0.09x** | 0.08x | cypy faster |

Summary: 7/7 picop faster · mean **0.19x** · median 0.12x.

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

**Order 067 — the C-function family and its subtype rule.** `PyCMethod_Type` is a real subtype of `PyCFunction_Type` (verified against the 3.14 headers: `tp_name = "builtin_method"`, `tp_base = builtin_function_or_method`), so `cfunction_check` (a `PyObject_TypeCheck`) accepts a `PyCMethod` while `cfunction_check_exact` does not — the pair is the discriminator, not a redundancy. `cmethod_check` is kept as an API even though the probe found **no** `PyCMethod` instance in the 3.14 stdlib (scanning the `__dict__` of `dict`, `list`, `str`, `int`, `object`, `OrderedDict`, `FrameType` returns zero): method descriptors, slot wrappers and bound builtins are all plain `PyCFunction` or their own types. The predicates therefore target extension types that build methods with `PyCMethod_New`, and Tier A has no honest baseline to time against, so both rows are recorded as `n/a` rather than guessed.

**Ownership and error contract.** `PyCFunction_GetSelf` returns a borrowed pointer, `NULL` for `METH_STATIC` / plain builtins, and raises `SystemError: Objects/methodobject.c:138: bad argument to internal function` when handed a non-C-function (`str.join`, `(1).__add__` both measured). The wrapper keeps the CPython error and promotes the borrowed self to an owned reference inside `cython.critical_section`, which is the free-threaded-safe way to read the field. `PyCFunction_GET_FUNCTION` is deliberately not exposed publicly: it yields a raw `PyCFunction` C pointer, which is not an object and cannot be incref'd or returned.

**Descriptor wrappers.** `classmethod_new` / `staticmethod_new` match the builtins exactly — they do **not** validate callability (`classmethod_new(1)` succeeds, as `classmethod(1)` does), so callers keep CPython's semantics. Tier A shows the win is structural: `classmethod(plain_func)` allocates the descriptor through Python's argument machinery (21.9 ms/80k) versus a direct `PyClassMethod_New` (4.5 ms), i.e. **0.20–0.21x**; Tier B narrows it to **0.09x** against a typed Cython baseline. Subtype note: `method_check` covers only Python bound methods (`PyMethod_Type`), never a `PyCFunction`/`PyCMethod`, which is why `cfunction_check` on a bound method returns True only for C-side methods.

**Why and scale.** Tier A: 11 measured operations, 10 wins, mean 0.48x; the only non-win is `method_new` at 1.02x, retained for API parity (binding from Cython without a Python call). Tier B: 7/7 wins, mean 0.19x. The `cfunction_get_self` Tier B p99× of 0.86x is the noisiest row — the baseline's own `__self__` descriptor lookup is already a fast path, so the margin there is the critical section, not the field read.

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

