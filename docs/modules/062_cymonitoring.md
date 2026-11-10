# cymonitoring

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython/monitoring.h` (PEP 670 C API, 3.13+) |
| Sources | `src/picop/cymonitoring.pxd`, `src/picop/cymonitoring_shim.h` |
| Surface | cimport |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

`sys.monitoring` is the Python-side half of PEP 670; the C header is the half an
extension needs when it *executes Python-like code* (a VM, a transpiler, a Cython
interpreter, a JIT). Registering a tool is pure Python, but emitting the events for
instructions the interpreter never saw is not: there is no supported way to say
"this synthetic code object just returned" without `PyMonitoring_*`.

Scope is the real cost, not the emit. Every event must be fired inside an entered
scope, the caller must own a `PyMonitoringState[19]` array, and the inline
`PyMonitoring_Fire*Event` wrappers already test `state->active`. The helper layer
does three things a hand-rolled version gets wrong: it enters the scope with the
complete 18-event table (so no slot is left uninitialised), it keeps the event id
constants in one place, and it makes the active gate explicit in the caller's loop.
The gate is worth 8x when nothing is watching (3.5 ns vs 29.6 ns) and costs nothing
when a tool is live (1.00x), which is the exact crossover this module was designed
for.

The earlier index-only pass declined this Order on the premise that "monitoring
state is interpreter-owned". That premise is wrong: `PyMonitoring_EnterScope` takes
a caller-supplied stack array, and the interpreter only reads it while the scope is
on the scope stack. Re-opened and measured.

## Inventory

Full surface of `cpython/monitoring.h`. No skim.

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| `PyMonitoringState` | C-API | struct | cimport | `{uint8_t active; uint8_t opaque;}`, 2 bytes |
| `PY_MONITORING_EVENT_PY_START` … `PY_MONITORING_EVENT_C_RAISE` | C-API | constants 0–17 | cimport | exported as-is through the shim |
| `PY_MONITORING_EVENT_BRANCH` (18) | C-API | constant | — | deprecated in 3.14, deliberately not declared |
| `PY_MONITORING_IS_INSTRUMENTED_EVENT(ev)` | C-API | macro | cimport | `monitoring_is_instrumented`; 3.14 tests `ev < _PY_MONITORING_LOCAL_EVENTS`, 3.15 tests `ev <= PY_MONITORING_EVENT_STOP_ITERATION` — same 0..10 range |
| `_PY_MONITORING_IS_UNGROUPED_EVENT(ev)` | used-by | macro (3.15 only) | — | internal; supports per-code-object enable/disable, no stable ABI |
| `PyMonitoring_EnterScope(state_array, version, event_types, length)` | C-API | function | wrapper `monitoring_scope` | array is caller-owned; `event_types` is positional (`state_array[i]` ↔ `event_types[i]`), ids outside 0..18 are skipped, `length` is not bounded |
| `PyMonitoring_ExitScope()` | C-API | function | wrapper `monitoring_exit_scope` | pops the scope, returns 0 |
| `PyMonitoring_FirePyStartEvent` … `PyMonitoring_FireStopIterationEvent` (17) | C-API | static inline | wrappers `fire_*` | inline `state->active` gate plus the underscore call |
| `_PyMonitoring_FirePyStartEvent` … `_PyMonitoring_FireStopIterationEvent` (17) | used-by | function | — | ungated; Tier B baseline only |
| `_PyMonitoring_FireBranchEvent` | C-API | function, `Py_DEPRECATED(3.14)` | — | rejected |
| `sys.monitoring` (`use_tool_id`, `register_callback`, `set_events`) | — | stdlib Python API | — | rejected: registration is not an acceleration target |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| `monitoring_scope` / `monitoring_exit_scope` | APPROVED (cimport) | scope discipline is the ABI contract; 1.03x–1.11x vs a hand-built array is the cost of always passing the full 18-id table |
| `monitoring_active` | APPROVED (cimport) | makes the gate explicit; measured as part of the fire rows |
| `monitoring_is_instrumented` | APPROVED (cimport) | macro → `cdef inline`, keeps the 3.14/3.15 spelling difference out of user code |
| `fire_py_start`, `fire_py_resume`, `fire_py_return`, `fire_py_yield`, `fire_call`, `fire_line`, `fire_jump`, `fire_branch_left`, `fire_branch_right`, `fire_c_return`, `fire_py_throw`, `fire_raise`, `fire_reraise`, `fire_exception_handled`, `fire_c_raise`, `fire_py_unwind`, `fire_stop_iteration` | APPROVED (cimport) | 0.12x against the ungated underscore call when no tool is watching; 0.99x–1.01x when one is |
| 18 `PY_MONITORING_EVENT_*` constants | APPROVED (cimport) | ids are literals in the shim; avoids pulling `cpython/monitoring.h` into every shim |
| `_PyMonitoring_Fire*Event` | REJECTED | internal entry points without the active gate; used only as the benchmark baseline |
| `PY_MONITORING_EVENT_BRANCH` / `_PyMonitoring_FireBranchEvent` | REJECTED | deprecated since 3.14; firing it writes a slot the interpreter never reads |
| `_PY_MONITORING_IS_UNGROUPED_EVENT` | REJECTED | private macro, 3.15-only, no public meaning |
| `sys.monitoring` registration wrapper | REJECTED | Python-side, not a hot path in compiled code |
| Tier A harness | n/a | no public Python-visible helper to time |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 2 |
| Last pass | 2026-11-09 — Tier B default and depth measured, smoke assertions added, SAFETY entry written |
| Next action | run the gates and merge; no public surface to index |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| `monitoring_scope` | a fixed 18-id scope beats hand-written per-site arrays | `bench/tier_b/cymonitoring.py` | 1.10x (3-id baseline), 1.10x (18-id baseline) | APPROVED (cimport) — clarity + correct slot coverage | 2 |
| `fire_py_return` | the inline gate is free when inactive | same harness, tool 4 enabled/disabled | 0.12x inactive, 1.00x with one tool live, 1.01x with two | APPROVED (cimport) | 2 |
| `monitoring_active` | gate placement matters more than the emit | measured inside the fire rows | gate saves 26 ns/fire on the inactive path | APPROVED (cimport) | 2 |
| raw `_PyMonitoring_Fire*` | skip the helper | same harness | 29.6 ns/fire vs 3.5 ns gated | REJECTED | 2 |
| `fire_branch_left`/`fire_branch_right` | BRANCH (18) is still usable | n/a | slot 18 is never written by `EnterScope`; deprecated in 3.14 | REJECTED | 2 |
| `monitoring_is_instrumented` | 3.14/3.15 macro spelling differs | compile probe against both header sets | both give 0..10 | APPROVED (cimport) | 2 |

## Bench notes

- Tier B harness: [`bench/tier_b/cymonitoring.py`](../../bench/tier_b/cymonitoring.py) — see [`bench/BENCH.md`](../../bench/BENCH.md)
- Harness: [`bench/tier_b/build.py`](../../bench/tier_b/build.py) (`python -m bench.tier_b.build cymonitoring`)
- Gate: [`docs/README.md`](../README.md) (mean ratio ≤ 0.95; cimport demote allowed)
- Env: CPython 3.15.0rc2, Linux x86_64, GIL build; Tier B default N=2,000,000 × 5 runs; depth pass N=8,000,000 × 5 runs
- No Tier A harness: the module has no public Python surface, so there is nothing to compare against plain Python.

## Bench results

### Tier B — default pass (N=2,000,000, 5 runs)

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| `monitoring_scope` + `monitoring_exit_scope` (18-event scope) | vs hand-rolled 3-id scope | 7.73±0.12ms | 7.82ms | 7.05±0.08ms | **1.10x** | 1.10x | baseline faster — scope width |
| `monitoring_scope` + `monitoring_exit_scope` (18-event scope) | vs hand-built 18-id scope | 7.66±0.23ms | 7.89ms | 6.94±0.13ms | **1.10x** | 1.10x | baseline faster — scope width |
| `fire_py_return` (inline gate) | no tool watching | 7.05±0.09ms | 7.14ms | 59.14±0.40ms | **0.12x** | 0.12x | cypy faster — gate wins |
| `fire_py_return` (inline gate) | 1 tool live | 260.25±3.22ms | 265.58ms | 259.57±1.28ms | **1.00x** | 1.02x | ~tie |
| `fire_py_return` (inline gate) | 2 tools live | 461.68±2.68ms | 464.50ms | 459.59±3.53ms | **1.00x** | 1.00x | ~tie |

Summary: 1/5 picop faster · 1/5 pass ≥5% gate · **mean ratio 0.87x** · median 1.00x.
Callback observation: 60,001,250 events reached the `sys.monitoring` callback.

### Tier B — depth pass (N=8,000,000, 5 runs)

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| scope enter+exit | vs hand-rolled 3-id scope | 34.80±2.84ms | 39.33ms | 33.66±0.61ms | **1.03x** | 1.14x | baseline faster |
| scope enter+exit | vs hand-built 18-id scope | 33.62±2.11ms | 36.86ms | 30.20±1.16ms | **1.11x** | 1.17x | baseline faster |
| `fire_py_return` (inline gate) | no tool watching | 29.82±2.08ms | 32.29ms | 253.33±3.78ms | **0.12x** | 0.12x | cypy faster |
| `fire_py_return` (inline gate) | 1 tool live | 1.050±0.017s | 1.072s | 1.048±0.014s | **1.00x** | 1.00x | ~tie |
| `fire_py_return` (inline gate) | 2 tools live | 1.832±0.008s | 1.845s | 1.859±0.025s | **0.99x** | 0.97x | ~tie |

Summary: 2/5 picop faster · 1/5 pass ≥5% gate · **mean ratio 0.85x** · median 1.00x.
Callback observation: 240,001,290 events.

Per-operation: the scope pair costs 3.9 ns (4.35 ns at depth) and an inactive `fire_py_return`
3.5 ns; the ungated underscore call costs 29.6 ns. Once a tool is live the callback
dispatch dominates (130 ns per fire) and the helper is indistinguishable from the
baseline.

## Experiment conclusions

- **Scale and threshold.** The win is entirely on the inactive path: 0.12x in both
  passes at N=2,000,000 and N=8,000,000. Once a tool is registered the ratio is
  1.00x/1.01x, because Python callback dispatch (≈130 ns) swamps the 26 ns saved by
  the gate. That is the crossover an author needs to know: the helper is free at
  worst and 8x cheaper when nothing is instrumented. The scope rows are 1.03x–1.11x
  against hand-rolled arrays, so the helper costs about 0.3 ns per scope enter to
  always pass the full 18-id table — the price of never leaving a slot stale.
- **Ownership and ABI.** `PyMonitoringState *` is borrowed: the caller owns the
  stack array and the interpreter only reads it while the scope is active. Cython
  does not zero `cdef PyMonitoringState states[19]` — an unentered array measured
  12 of 19 `active` bytes non-zero. Probing with the array pre-filled to a sentinel
  pinned the semantics: `event_types` is **positional** (`state_array[i]` is
  populated for `event_types[i]`), so ids `[LINE, PY_RETURN]` with `length == 2`
  wrote slots 0 and 1, not 5 and 2 — the shim's table is `0..17` in id order, which
  is what makes slot `i` mean event `i`. `length` is unbounded (100 ids returned 0)
  and an id outside 0..18 is silently skipped (id 255 left its slot at the sentinel),
  so a malformed table never raises. Slot 18 (`PY_MONITORING_EVENT_BRANCH`,
  deprecated in 3.14) is never written. The `version` argument is a memo: when it
  already equals the interpreter's monitoring version, `EnterScope` returns 0
  **without populating the array** — measured with a fresh array, `version = 0`, and
  no tool ever enabled. Nothing fires in that state, so correctness is safe, but the
  caller-side gate reads stack garbage and stops saving anything; `memset` the array
  if the first scope in a process matters.
- **Header drift.** 3.15 changed the `monitoring.h` include guard from
  "must not be included directly" to `Py_MONITORING_H` and rewrote
  `PY_MONITORING_IS_INSTRUMENTED_EVENT` from `ev < _PY_MONITORING_LOCAL_EVENTS` to
  `ev <= PY_MONITORING_EVENT_STOP_ITERATION`. Both resolve to the same 0..10 set, so
  `monitoring_is_instrumented` is portable across the 3.14/3.15 CI matrix; the shim
  does not depend on either spelling.
- **Demote rationale.** Nothing is demoted: there is no public surface, so the cimport
  rule is satisfied by design. `PyMonitoringState` and the event constants are in the
  barrel `__init__.pxd` so out-of-tree extensions get them from `from picop cimport …`
  — verified by the smoke run, which cimports through the barrel and asserts both the
  active and inactive gate paths against a real `sys.monitoring` callback.
- **Free-threading.** The scope stack is per-thread; the helpers take the GIL and are
  safe under both builds (the smoke script runs the assertions in the free-threaded
  CI leg). `fire_*` returns `-1` and propagates the exception when a callback raises,
  so a raising tool callback does not silently continue the loop.

## Done when

- [x] Full inventory vs mapped include (`cpython/monitoring.h` — all 19 event ids, both scope functions, 17 fire wrappers, 17 underscore internals, 2 internal macros)
- [x] Every row has workflow status
- [x] Lifecycle + next action filled
- [x] APPROVED (cimport) rows have decision-log evidence
- [x] REJECTED rows have policy or measured why
- [x] Present measuring: try-all and depth checklist in Experiment conclusions
- [x] Bench results table filled in this file (default and depth passes)
- [x] No `.pyi` needed (cimport-only); `.pxd` lean — event ids in the shim, types in the `.pxd`
