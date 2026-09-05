# cygc.pxd
# ``PyGC_*`` tuning helpers. Public docs: ``cygc.pyi``.
# Track/UnTrack/New* are type-object plumbing — not wrapped.

cdef extern from "Python.h":
    Py_ssize_t PyGC_Collect() except -1
    int PyGC_Enable() except -1
    int PyGC_Disable() except -1
    int PyGC_IsEnabled() except -1


cdef inline Py_ssize_t gc_collect_c() noexcept:
    return PyGC_Collect()


cdef inline bint gc_is_enabled_c() noexcept:
    return PyGC_IsEnabled() != 0


cdef inline int gc_enable_c() noexcept:
    return PyGC_Enable()


cdef inline int gc_disable_c() noexcept:
    return PyGC_Disable()


cpdef inline Py_ssize_t gc_collect() noexcept:
    return gc_collect_c()


cpdef inline bint gc_is_enabled() noexcept:
    return gc_is_enabled_c()


cpdef inline int gc_enable() noexcept:
    # Returns prior enabled flag (0/1).
    return gc_enable_c()


cpdef inline int gc_disable() noexcept:
    # Returns prior enabled flag (0/1).
    return gc_disable_c()
