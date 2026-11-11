# Explicit critical sections (Order 70)

`with cython.critical_section(obj):` is still the default. `cycriticalsection` is for
the two shapes that syntax cannot express: a section whose lifetime is not a lexical
block, and a section guarded by a mutex you own instead of by a Python object.

```cython
from picop cimport PyMutex, mutex_init
from picop.cycriticalsection cimport (
    PicopCriticalSection,
    critical_sections_enabled,
    cs_begin,
    cs_begin_mutex,
    cs_end,
)

cdef struct Cache:
    PyMutex lock
    long hits

cpdef long bump(long iterations):
    cdef Cache cache = Cache()   # zero-initialises the struct
    cdef PicopCriticalSection cs
    cdef long i
    mutex_init(&cache.lock)
    for i in range(iterations):
        cs_begin_mutex(&cs, &cache.lock)   # guard a C struct field, not an object
        cache.hits += 1
        cs_end(&cs)                        # the section ends here, not at a block end
    return cache.hits
```

Rules:

- `cdef PicopCriticalSection cs` is a stack buffer. It is opaque: the shim sizes it
  generously and never reads it, so a section may be entered and exited around any
  control flow, but one buffer must be paired `begin`/`end` before it is reused.
- A `cdef` C struct on the stack is **not** zero-initialised by Cython. Write
  `cdef Cache cache = Cache()` (or assign every field) before locking it.
- Sections nest. `cs_begin(&outer, obj)` then `cs_begin(&inner, obj)` does **not**
  deadlock on the same object mutex — CPython suspends the outer protection and
  resumes it at `cs_end(&inner)`.
- In a GIL build every wrapper is a no-op, exactly as in CPython. Use
  `critical_sections_enabled()` to branch on the build, never as a lock.
- The mutex is borrowed: it must outlive the section, and `cs_end` releases it.

Measured cost on CPython 3.15 free-threaded (see the tracker): `cs_begin_mutex` /
`cs_end` is 1.61x a bare `mutex_lock` / `mutex_unlock` pair, because a critical
section registers the guarded mutex on the thread state so nested sections can
suspend and resume it. If you do not need that semantics, call `cylock` directly.

The out-of-tree smoke exercises the whole surface, including nested sections on the
same object: [`../cimport_ext/demo.pyx`](../cimport_ext/demo.pyx).

Full inventory and bench evidence:
[`docs/modules/070_cycriticalsection.md`](../../docs/modules/070_cycriticalsection.md).
