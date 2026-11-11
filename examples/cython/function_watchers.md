# Function watchers (Order 71)

`PyFunction_AddWatcher` / `PyFunction_ClearWatcher` (CPython 3.12+) give a compiled
extension a per-interpreter hook on function lifetimes: creation, destruction, and
replacement of a function's `__code__`, `__defaults__`, `__kwdefaults__`, and (3.15+)
`__qualname__`. There is no Python-level equivalent, so the surface is cimport-only.

```cython
from cpython.object cimport PyObject
from picop.cyfunction cimport (
    func_add_watcher,
    func_clear_watcher,
    PyFunctionObject,
    PyFunction_WatchEvent,
    PyFunction_EVENT_DESTROY,
    PyFunction_EVENT_MODIFY_KWDEFAULTS,
)

cdef PyFunctionObject *_tracked = NULL
cdef int _handle = -1
cdef bint _destroyed = False

cdef int _on_function_event(PyFunction_WatchEvent event,
                            PyFunctionObject *func,
                            PyObject *new_value) except -1:
    global _tracked, _destroyed
    # No Python API calls: preserve pending exceptions and never resurrect func.
    if func == _tracked and event == PyFunction_EVENT_DESTROY:
        _tracked = NULL
        _destroyed = True
    return 0

cpdef void track(object function):
    global _handle, _tracked, _destroyed
    if _handle >= 0:
        raise RuntimeError("already tracking a function")
    _handle = func_add_watcher(_on_function_event)
    _tracked = <PyFunctionObject*>function
    _destroyed = False

cpdef void untrack():
    global _handle, _tracked
    _tracked = NULL
    if _handle >= 0:
        func_clear_watcher(_handle)
        _handle = -1
```

Rules:

- The callback is a C function pointer. Write it as `cdef int ... except -1`: if it
  raises, Cython returns `-1` and CPython reports an unraisable exception; this
  does not veto the mutation. Preserve any exception already pending on entry.
  The declared type is `except -1`, so a `noexcept` callback will not assign to it —
  even a no-op hook must use `except -1`.
- Assign the handle and the tracked pointer at module scope, and declare them
  `global` inside the function that sets them: without `global`, Cython creates a
  local C variable and the callback keeps seeing the stale module-level pointer.
- Watchers only fire for real `PyFunctionObject` instances. A `def` in a Cython
  module is a `cyfunction`, so mutating its `__defaults__` produces no event; the
  demo builds its sample with `compile()`/`exec()` for that reason.
- Registration is global to the interpreter, not to one function. Every function that
  is created, destroyed, or modified while the watcher is registered fires the hook,
  including functions built by other modules — filter by identity (`func == _tracked`)
  or keep a set, rather than assuming the event belongs to your own object.
- The handle returned by `func_add_watcher` is what `func_clear_watcher` expects,
  and each handle must be cleared exactly once.
- CPython keeps 8 watcher slots per interpreter (measured on 3.14 and 3.15t).
  Register at module import and clear on shutdown: `func_add_watcher` raises
  `RuntimeError: no more func watcher IDs available` when the table is full.
- `func_clear_watcher` raises `ValueError` for an id that is out of range or
  already cleared — clearing twice is an error, so clear exactly once.
- Do not retain `func` during `DESTROY`: taking a reference resurrects it.
  The callback above only updates C state and clears the borrowed pointer.
- `PyFunction_EVENT_MODIFY_QUALNAME` exists only on CPython 3.15+. Cython cannot
  probe a C enum member at compile time, so picop exposes
  `func_event_modify_qualname()`, which returns the event id on 3.15+ and `-1`
  on 3.14:

```cython
qualname_event = func_event_modify_qualname()
if qualname_event >= 0:
    expected.append((qualname_event, "renamed"))
```

The out-of-tree smoke exercises the whole surface on 3.14 (GIL) and 3.15t
(free-threaded), including `CREATE`/`DESTROY` for `exec`-compiled functions:
[`../cimport_ext/demo.pyx`](../cimport_ext/demo.pyx).

Full inventory and bench evidence:
[`docs/modules/029_cyfunction.md`](../../docs/modules/029_cyfunction.md).
