# cyfunction

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.function` |
| Sources | `src/picop/cyfunction.pxd`, `.pyx`, `.pyi`, `src/picop/cyfunction_shim.h` |
| Surface | public |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Function-object checks and field accessors beat attribute lookup from Python.

## Inventory

Full `cpython/function` surface, including the unchecked macros kept cimport-only.

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| `PyFunction_Check` | C-API | macro | `func_check` | exact type check; the function type is not subclassable |
| `PyFunction_New` | C-API | function | `func_new` | validates `code` / `globals` before construction |
| `PyFunction_NewWithQualName` | C-API | function | `func_new_with_qualname` | the compiler path for nested defs — `__qualname__` correct from the start |
| `PyFunction_GetCode` / `GetGlobals` / `GetModule` / `GetDefaults` / `GetClosure` / `GetKwDefaults` / `GetAnnotations` | C-API | function | public getters | borrowed `PyObject *` promoted to an owned reference under `cython.critical_section` |
| `PyFunction_SetDefaults` / `SetClosure` / `SetKwDefaults` / `SetAnnotations` | C-API | function | public setters | status int, `0` on success; errors raise — never read the status as a bool |
| `PyFunction_GET_CODE` / `GET_GLOBALS` / `GET_MODULE` / `GET_DEFAULTS` / `GET_CLOSURE` / `GET_KW_DEFAULTS` / `GET_ANNOTATIONS` | C-API | macro | cimport-only `*_unchecked` | no type check, borrowed field refs; trusted caller only |
| `func_eq` / `funceq` | cypy | helper | public / soft alias | identity equality (`object.__eq__` for functions); not on `hot` |
| `PyFunction_AddWatcher` | C-API | function | cimport `func_add_watcher` | registers a per-interpreter lifecycle callback; returns the handle, raises when the watcher table is full |
| `PyFunction_ClearWatcher` | C-API | function | cimport `func_clear_watcher` | clears one handle; `ValueError` for an unknown or already-cleared id |
| `PyFunction_WatchEvent` (`CREATE`, `DESTROY`, `MODIFY_CODE`, `MODIFY_DEFAULTS`, `MODIFY_KWDEFAULTS`) | C-API | enum | cimport constants | re-exported as a Cython enum so callbacks match the C signature exactly; `MODIFY_QUALNAME` is 3.15+ |
| `PyFunction_WatchCallback` | C-API | function-pointer typedef | cimport type | `cdef int …(PyFunction_WatchEvent, PyFunctionObject *, PyObject *) except -1`; callback errors are reported as unraisable, not mutation vetoes |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| func_check / get_code / globals / defaults | APPROVED | **0.40–0.63x** |
| func_new / set_* | APPROVED (API) | construction / mutation completeness |
| func_eq / funceq | APPROVED | identity equality (issue #40); not `hot` |
| func_get_module / func_get_closure | APPROVED | Tier A wins in the Order 067 try-all pass |
| func_get_kw_defaults / func_set_kw_defaults | APPROVED | Tier A **0.54x** / Tier B **0.36x**; keyword-only defaults had no accessor before |
| func_get_annotations / func_set_annotations | APPROVED | Tier A **0.41–0.44x**; `None` when unset (distinct from the lazily created `__annotations__` dict) |
| func_new_with_qualname | APPROVED | Tier A **0.24x**, Tier B **0.48x** |
| `PyFunction_GET_*` macros | APPROVED (cimport) | unchecked, borrowed field refs; deliberately not public |
| `func_new` / `func_new_with_qualname` argument validation | APPROVED | `TypeError` instead of CPython's `SystemError` for a non-code / non-dict argument |
| `func_add_watcher` / `func_clear_watcher` (Order 071) | APPROVED (cimport) | no Python-level equivalent exists; a Python-callable version would need a trampoline holding every callback alive, and the event stream is interpreter-global, so only compiled callers can bound it |
| `PyFunction_WatchEvent` enum re-export | APPROVED (cimport) | declaring the members with their real types is what makes a Cython `cdef` callback match `PyFunction_WatchCallback`; the earlier `int`/`PyObject *` spelling fails to compile against the C typedef |
| `PyFunction_EVENT_MODIFY_QUALNAME` unguarded use | REJECTED (as a plain constant) | 3.15+ only; use `func_event_modify_qualname()` for code that must compile on 3.14 |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 3 |
| Last pass | 2026-11-11 — Order 071: watcher registration, clearing, version-gated qualname event; Tier B dispatch cost and 3.14/3.15t cimport smoke |
| Next action | — |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| check/getters | 0.40–0.63x | Tier A | pass | APPROVED | 1 |
| new/set | API | — | API | APPROVED (API) | 1 |
| func_eq / funceq | identity | Tier A + Tier B | 0.54x / 0.41–0.50x | APPROVED | 1 |
| kw-defaults + annotations accessors | keyword-only defaults and annotations are unreachable without attribute lookup in Cython | Tier A try-all + Tier B | 10/10 faster, mean **0.47x**; Tier B 9/9, mean **0.27x** | APPROVED | 2 |
| `func_new_with_qualname` | the qualname-aware constructor beats constructing then patching | Tier A + Tier B | 0.24x / 0.48x | APPROVED | 2 |
| `func_new` validation | CPython's unchecked C entry points surface `SystemError` for bad arguments | probe: `func_new(1, {})` | `SystemError` before, `TypeError` after | APPROVED | 2 |
| `PyFunction_GET_*` macros | public unchecked getters invite misuse on non-functions | probe: `func_get_code(len)` raises `SystemError` | kept cimport-only | APPROVED (cimport) | 2 |
| watcher registration / clearing | expose interpreter lifecycle hooks without a Python trampoline | Tier B dispatch + cimport smoke | watched setters 1.57–1.59x; construction 1.13x; lifecycle and clear errors verified | APPROVED (cimport) | 3 |
| `func_event_modify_qualname` | one source compiles on both supported versions | cimport smoke + probe | -1 on 3.14; 5 on 3.15t | APPROVED (cimport) | 3 |

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

### Order 067 pass (Tier A try-all)

Harness: [`bench/cyfunction_bench.py`](../../bench/cyfunction_bench.py) · CPython 3.14 · Linux x86_64 · GIL build · `N=80_000` × `runs=5`

| operation | case | picop mean±σ | p99 | baseline mean±σ | p99 | ratio | p99× | verdict |
|---|---|---:|---:|---:|---:|---:|---:|---|
| func_check | function | 2.37±0.13ms | 2.59ms | 5.06±0.11ms | 5.16ms | **0.47x** | 0.50x | pass |
| func_check | builtin | 2.93±1.29ms | 5.11ms | 7.04±1.06ms | 8.47ms | **0.42x** | 0.60x | pass |
| func_get_code | `__code__` | 2.62±0.00ms | 2.62ms | 5.24±0.68ms | 6.39ms | **0.50x** | 0.41x | pass |
| func_get_globals | `__globals__` | 2.69±0.02ms | 2.72ms | 3.74±0.71ms | 4.95ms | **0.72x** | 0.55x | pass |
| func_get_defaults | `__defaults__` | 2.61±0.00ms | 2.61ms | 5.02±0.05ms | 5.06ms | **0.52x** | 0.52x | pass |
| func_get_kw_defaults | `__kwdefaults__` | 2.97±0.75ms | 4.24ms | 5.51±0.54ms | 6.36ms | **0.54x** | 0.67x | pass |
| func_set_kw_defaults | dict swap | 2.97±0.02ms | 3.00ms | 7.30±1.51ms | 9.86ms | **0.41x** | 0.30x | pass |
| func_get_annotations | unset | 2.62±0.03ms | 2.65ms | 6.46±0.64ms | 7.54ms | **0.41x** | 0.35x | pass |
| func_get_annotations | set dict | 2.98±0.02ms | 3.00ms | 6.81±0.62ms | 7.69ms | **0.44x** | 0.39x | pass |
| func_new_with_qualname | code + globals + qualname | 7.01±0.09ms | 7.12ms | 28.68±1.33ms | 30.62ms | **0.24x** | 0.23x | pass |

Summary: 10/10 picop faster · mean **0.47x** · median 0.45x.

### Order 067 pass (Tier B)

Harness: [`bench/tier_b/cyfunction.py`](../../bench/tier_b/cyfunction.py) · `cyfunction_tb.pyx` · `CPY_TIERB_N=2_000_000` × `runs=5`

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| func_check | def | 2.68±0.04ms | 2.72ms | 20.98±0.36ms | **0.13x** | 0.13x | cypy faster |
| func_get_code | def | 9.96±0.44ms | 10.67ms | 34.21±0.68ms | **0.29x** | 0.30x | cypy faster |
| func_get_code | def (unchecked macro) | 5.53±0.10ms | 5.68ms | 34.01±0.50ms | **0.16x** | 0.16x | macro baseline |
| func_get_kw_defaults | def | 11.80±0.13ms | 11.99ms | 33.17±0.55ms | **0.36x** | 0.35x | cypy faster |
| func_get_kw_defaults | def (unchecked macro) | 4.16±0.15ms | 4.34ms | 32.99±0.54ms | **0.13x** | 0.13x | macro baseline |
| func_get_annotations | def | 9.91±0.26ms | 10.31ms | 30.81±0.34ms | **0.32x** | 0.33x | cypy faster |
| func_get_annotations | def (unchecked macro) | 5.42±0.08ms | 5.55ms | 30.59±0.25ms | **0.18x** | 0.18x | macro baseline |
| func_set_kw_defaults | dict | 15.72±0.14ms | 15.87ms | 43.30±0.29ms | **0.36x** | 0.36x | cypy faster |
| func_new_with_qualname | code + globals + qualname | 103.68±0.35ms | 103.90ms | 215.86±1.14ms | **0.48x** | 0.48x | cypy faster |

Summary: 9/9 picop faster · mean **0.27x** · median 0.29x.

### Order 071 pass (Tier B — watcher dispatch cost)

Harness: [`bench/tier_b/cyfunction.py`](../../bench/tier_b/cyfunction.py) · `cyfunction_tb.pyx` · CPython 3.14.7 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`
Same mutation loop, watcher registered or not — ratio = watched / unwatched. **Informational**: watchers are a cost, not a win.

| operation | case | cypy mean±σ | p99 | unwatched mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|------------------|-------|------|------|
| func_set_kw_defaults (counting watcher) | vs unwatched setter | 23.72±0.44ms | 24.08ms | 14.92±0.26ms | **1.59x** | 1.58x | baseline faster |
| func_set_kw_defaults (no-op watcher) | vs unwatched setter | 23.32±0.32ms | 23.74ms | 14.90±0.41ms | **1.57x** | 1.55x | baseline faster |
| func_new_with_qualname (watcher registered) | vs unwatched constructor | 121.55±0.73ms | 122.28ms | 107.81±0.61ms | **1.13x** | 1.13x | baseline faster |

**Takeaway:** watched setters cost **1.57–1.59x** and watched construction **1.13x** in this pass. The no-op and counting callbacks have similar cost; these are dispatch-cost measurements, not speedup claims.

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

**Order 067 — ownership, ABI, and the qualname constructor.** Every `PyFunction_Get*` accessor returns a *borrowed* pointer; the public getters promote it to an owned reference under `cython.critical_section` so the returned object survives the call under free-threaded builds. `func_get_annotations` returns `None` when the annotation slot is uninitialised, which is *not* the same as `f.__annotations__` — attribute access lazily creates an empty dict, so a caller that branches on `None` gets the C-level state, not a synthesised one. `PyFunction_Set*` returns `0`/`-1`; the wrappers raise on `-1`, so the status must never be read as a boolean. `func_new` and `func_new_with_qualname` now reject a non-code object or a non-dict globals before entering `PyFunction_New`: without that guard CPython's unchecked internals surface `SystemError: bad argument to internal function` (measured: `func_new(1, {})`), which is indistinguishable from a real internal fault. `func_new_with_qualname` is the compiler's own path for nested defs and is 0.24x Tier A against building the function and patching `__qualname__`.

**Order 071 — watcher ownership and errors.** `PyFunction_AddWatcher` registers a C callback interpreter-wide, so consumers must filter unrelated function events. `func` and non-NULL `new_value` are borrowed pointers; the event argument is an enum, not a reference. The callback may inspect but must not modify the function. CREATE occurs after initialization; modification and DESTROY notifications precede the operation. Retaining the function during DESTROY resurrects it, so the recipe clears its borrowed pointer and records only C state. Callback exceptions are reported as unraisable rather than vetoing mutation; callbacks must preserve any pending exception on entry ([CPython contract](https://docs.python.org/3.14/c-api/function.html#c.PyFunction_WatchCallback)). The version shim returns -1 on 3.14 and 5 on 3.15t. Cython callbacks use the declared `except -1` signature, and assignment to the module-level tracked pointer requires `global`. Probes on 3.14 and 3.15t observed eight watcher slots, `RuntimeError` on exhaustion, and `ValueError` on invalid or already-cleared handles. Both cimport smoke runs passed, including genuine no-GIL execution on 3.15t.

**Cython-compiled code objects.** Wrapping a `__code__` produced by a Cython `.pyx` module in `func_new` is unsafe: the call aborts with `Fatal Python error: _TAIL_CALL_CACHE: Executing a cache` because Cython code objects carry frame-cache assumptions that a plain `PyFunction` does not set up. Pure-Python code (`compile(...)` / a `.py` function) is fine — the barrel demo in `examples/cimport_ext/demo.pyx` builds its sample with `compile()` for exactly this reason.

**Why and scale.** Tier A try-all is 10/10 faster (mean 0.47x); the weakest case is `func_get_globals` at 0.72x, still well inside the 0.95 gate. Tier B is informational and stronger (mean 0.27x): the unchecked macro variants show how much of the checked-getter cost is the type guard plus the critical-section round trip rather than the field read itself.

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
