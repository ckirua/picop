# cytime.pxd
# High-resolution clocks. Public docs in ``cytime.pyi``.
# Prefer this module over deferring to cycel.time for cypy surface.

cdef extern from "Python.h":
    ctypedef long long PyTime_t
    int PyTime_Time(PyTime_t *result) except -1
    int PyTime_Monotonic(PyTime_t *result) except -1
    int PyTime_PerfCounter(PyTime_t *result) except -1
    double PyTime_AsSecondsDouble(PyTime_t t) noexcept


cdef inline object time_time():
    cdef PyTime_t t
    PyTime_Time(&t)
    return PyTime_AsSecondsDouble(t)


cpdef inline object time_monotonic():
    cdef PyTime_t t
    PyTime_Monotonic(&t)
    return PyTime_AsSecondsDouble(t)


cpdef inline object time_perf_counter():
    cdef PyTime_t t
    PyTime_PerfCounter(&t)
    return PyTime_AsSecondsDouble(t)


cdef inline int time_time_raw(PyTime_t *result) except -1:
    return PyTime_Time(result)


cdef inline int time_monotonic_raw(PyTime_t *result) except -1:
    return PyTime_Monotonic(result)


cdef inline int time_perf_counter_raw(PyTime_t *result) except -1:
    return PyTime_PerfCounter(result)


cdef inline double time_as_seconds(PyTime_t t) noexcept:
    return PyTime_AsSecondsDouble(t)

# N6: preferred time_wall (0.3: time_time cdef-only)
cpdef inline object time_wall():
    return time_time()
