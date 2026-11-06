# Locks: `critical_section` vs a typed `PyMutex` (Order 63)

`cython.critical_section` is the right tool when the thing you protect is a Python
object. `cylock` is for the cases Cython cannot express: a mutex that lives in a C
struct, one shared with a library, or one you must hold across a section that has
already dropped the GIL.

```cython
from picop cimport PyMutex, mutex_init, mutex_lock, mutex_unlock, mutex_is_locked

cdef struct Shard:
    PyMutex lock
    long total

cdef void shard_add(Shard *s, long value) noexcept nogil:
    mutex_lock(&s.lock)
    s.total += value
    mutex_unlock(&s.lock)

cpdef long shard_drain(long iterations):
    cdef Shard shard
    cdef long i
    mutex_init(&shard.lock)
    with nogil:
        for i in range(iterations):
            shard_add(&shard, i)
    return shard.total
```

Rules:

- Declare the mutex where the critical section lives. `PyMutex` is a value, not an
  object — picop only ever borrows `PyMutex *`.
- `PyMutex` is **not** reentrant: locking a mutex this thread already holds parks it.
- `mutex_is_locked` is a diagnostic, not a locking primitive. It says "someone holds
  it", never "it is safe for me to take it".

The out-of-tree smoke exercises exactly this:
[`../cimport_ext/demo.pyx`](../cimport_ext/demo.pyx) holds a module-level mutex in
one thread while another thread reads its state.

Full inventory and safety notes:
[`docs/modules/063_cylock.md`](../../docs/modules/063_cylock.md).
