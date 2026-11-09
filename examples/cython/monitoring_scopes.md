# cymonitoring — monitoring scopes in Cython

An extension that emulates Python execution must enter a monitoring scope before
checking event masks or firing events. The scope snapshots the active tools for
the current execution context, allowing fire helpers to avoid the interpreter
fire path when no tool is watching.

Allocate one `PyMonitoringState` slot for each of the 19 event ids and maintain
a version counter for the scope. The array is **not** zero-initialised by Cython:
`monitoring_scope` fills slots 0..17, and slot 18 (`PY_MONITORING_EVENT_BRANCH`,
deprecated in 3.14) is never written — use the separate `BRANCH_LEFT` and
`BRANCH_RIGHT` events.

Two ABI details worth knowing before writing your own scope (measured on 3.15 with
the array pre-filled to a sentinel):

- `event_types` is positional: `state_array[i]` is filled for `event_types[i]`, so
  the table has to be in event-id order. `cypy_monitoring_all_events` is `0..17`.
- `version` is a memo. If it already matches the interpreter's monitoring version,
  `EnterScope` returns 0 without touching the array — which is what happens on the
  first scope of a process where nothing has ever been instrumented. The interpreter
  fires nothing in that case, but `monitoring_active` reads stack garbage and the
  gate stops helping. `memset(states, 0, sizeof(states))` if you need the gate to be
  exact from the first call.

```cython
from picop cimport (
    PyMonitoringState,
    monitoring_scope,
    monitoring_exit_scope,
    monitoring_active,
    fire_line,
    PY_MONITORING_EVENT_LINE,
)

cdef PyMonitoringState states[19]
cdef unsigned long long version = 0
monitoring_scope(states, &version)
if monitoring_active(states, PY_MONITORING_EVENT_LINE):
    fire_line(states, codelike, offset, lineno)
monitoring_exit_scope()
```

Measured on CPython 3.15 (Tier B, inner loop `N=2,000,000`): scope enter plus
exit was 3.9 ns versus 3.5 ns for a hand-rolled three-id array (1.10x). A
`fire_py_return` with no watchers took 3.5 ns versus 29.6 ns for an ungated
`_PyMonitoring_FirePyReturnEvent` call (0.12x). With one active tool, both paths
took 130 ns; with two active tools, 231 ns versus 229 ns (1.00x).
