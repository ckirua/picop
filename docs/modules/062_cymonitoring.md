# cymonitoring

| Field | Value |
|-------|--------|
| Status | absent |
| Maps to | `cpython/monitoring.h` (PEP 670) |
| Sources | — |
| Surface | none |
| Tracker lifecycle | indexed (decided-and-decline) |
| Format | v2 |
| Indexed | full |

## Why

Order 062 examined the PEP 670 monitoring surface: `PyMonitoring_EnterScope` /
`PyMonitoring_ExitScope` plus the `_PyMonitoring_Fire*` family (PyStart, PyResume,
PyReturn, PyYield, Call, Line, Jump, Branch, CCall, CReturn, CLine, Intrinsic,
SetLocal, Exception, UnresolvedLocal, Return, Instruction). Every one of those
functions takes a `PyMonitoringState *` owned by the interpreter and fires events
into the hook machinery that `sys.monitoring` already drives. Wrapping them would
mean picop owning event registration and dispatch, which competes with the
standard library and gives callers nothing they cannot get from
`sys.monitoring.register()`. The state array is also interpreter-owned and
version-gated (`uint64_t *version`), so a borrowed pointer from a helper would be
a refcount/GIL safety problem rather than a hot-path win.

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| `PyMonitoring_EnterScope` | C-API | candidate | — | takes the interpreter state array + version counter |
| `PyMonitoring_ExitScope` | C-API | candidate | — | global scope bookkeeping |
| `_PyMonitoring_FirePyStartEvent` … `_PyMonitoring_FireInstructionEvent` | C-API | candidate | — | underscore-prefixed; internal dispatch entry points |
| `PyMonitoringState` | C-API | candidate | — | interpreter-owned struct, not a Python object |
| `sys.monitoring` | Python | existing | — | the supported way to observe events |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| monitoring event wrappers | REJECTED | duplicates `sys.monitoring`; requires owning interpreter state |
| `PyMonitoring_EnterScope` / `ExitScope` | REJECTED | scope/version semantics are internal; misuse corrupts event state |

## Lifecycle

| Field | Value |
|-------|--------|
| Freeze | n/a — no surface added |
| Iteration | 1 |
| Last pass | 2026-11-05 — header diff against CPython 3.15 headers |
| Next action | reopen only if a caller needs a C-level event hook without `sys.monitoring` |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| monitoring wrappers | faster event plumbing for extensions | path or — | no measurable path; state is interpreter-owned | REJECTED | 1 |

## Bench notes

- No harness: nothing on this surface is measurable as a helper call.
- Gate: [`docs/README.md`](../README.md) — not applicable, no public helper.

## Bench results

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| — | — | — | — | — | — | REJECTED ABI — no wrapper, no harness |

## Experiment conclusions

Diffing CPython 3.15 `cpython/monitoring.h` against the 61 `src/picop/*.pxd`
modules is the only way this header stayed uncovered: Cython ships no
`monitoring.pxd`, so the surface is genuinely unwrapped, not merely unmeasured.

| Topic | Finding |
|-------|---------|
| Ownership | `PyMonitoringState` lives in the interpreter; a picop helper would hold borrowed, version-stamped state |
| Free-threading / GIL | event dispatch is already serialised by the runtime; wrapping it adds no lock safety |
| ABI | the `Fire*` entry points are underscore-prefixed internal APIs, not stable public ABI |
| Safety | registering hooks from C without `sys.monitoring` risks double-registration and lost events |

**Decision:** decline. Keep the header unwrapped; `sys.monitoring` is the supported
path. If a future Order needs C-level hooks, it must first define a picop-owned
event state, which is a policy change, not a helper.

## Done when

- [x] Full inventory vs mapped include
- [x] Every row has workflow status
- [x] Lifecycle + next action filled
- [x] REJECTED rows have policy or measured why
