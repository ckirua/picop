# Dict watchers (Order 72)

`PyDict_AddWatcher` / `PyDict_Watch` (CPython 3.12+) give a compiled extension a
per-interpreter hook on the lifetime of specific dictionaries: item added,
modified, deleted, key-layout cloned, cleared, and the dict deallocated. There
is no Python-level equivalent, so the picop surface is cimport-only.

```cython
from cpython.object cimport PyObject
from picop.cydict cimport (
    dict_add_watcher,
    dict_clear_watcher,
    dict_watch,
    dict_unwatch,
    PyDict_WatchEvent,
    PyDict_EVENT_ADDED,
    PyDict_EVENT_MODIFIED,
    PyDict_EVENT_DELETED,
)

cdef dict _registry = {}
cdef int _handle = -1

cdef int _on_dict_event(PyDict_WatchEvent event, PyObject *d, PyObject *key, PyObject *value) except -1:
    # No Python API calls: preserve pending exceptions and never mutate `d`.
    global _registry
    if key is not NULL:
        _registry[<object>key] = int(event)
    return 0

cpdef void observe(dict registry_dict):
    global _handle
    if _handle >= 0:
        raise RuntimeError("already observing")
    _handle = dict_add_watcher(_on_dict_event)
    dict_watch(registry_dict, _handle)

cpdef void stop():
    global _handle, _registry
    _registry.clear()
    if _handle >= 0:
        dict_clear_watcher(_handle)
        _handle = -1
```

Rules:

- The callback is a C function pointer declared `cdef int ... except -1`. If it
  raises, Cython returns `-1` and CPython reports an unraisable exception; the
  mutation is **not** vetoed. Preserve any exception already pending on entry.
- `dict` / `key` / `new_value` are borrowed references. CLEARED and DEALLOCATED
  pass NULL key and value. Inspect only — never mutate the watched dict from
  the callback (re-entry into the same dict is undefined).
- Registration is per-interpreter and global: the handle sees **only dicts
  explicitly marked with `dict_watch`**. Mark each dict you care about, and
  `dict_unwatch` before teardown so deallocation noise stops.
- CPython keeps 8 watcher slots; ids **2..7** are the user slots (0 and 1 are
  reserved for CPython itself). `dict_add_watcher` raises `RuntimeError` when
  the table is full (measured on 3.14 and 3.15t). `dict_clear_watcher` raises
  `ValueError` for an out-of-range or already-cleared id — clear exactly once.
- `CLONED` is not "someone copied my dict". It fires on the **watched target**
  when an empty watched dict merges another dict and adopts its keys:

```cython
d.clear()          # CLEARED
d.update(src)      # CLONED, key = src (the source dict), value NULL
```

  A copy of a watched dict is *not* watched: `other = d.copy()` fires nothing.
- Every mutation of a watched dict goes through the tag check; Tier B measured
  the whole watcher dispatch (register, watch, per-set callback, unwatch,
  clear) at ~1% of an unwatched set loop. Watching is cheap; the per-event
  callback is the only real cost.
- Watchers fire identically on 3.14, 3.15, and true no-GIL 3.15t. In
  free-threaded builds registration/clearing serialize on the interpreter's
  watcher mutex; the callback still runs on whichever thread performed the
  mutation, so keep the callback thread-safe (C state only, or a lock).

Evidence and bench tables:
[`docs/modules/003_cydict.md`](../../docs/modules/003_cydict.md).
Live probe: `check_dict_watchers()` in
[`examples/cimport_ext/demo.pyx`](../cimport_ext/demo.pyx), run by
[`scripts/smoke_barrel_cimport.sh`](../../scripts/smoke_barrel_cimport.sh).