# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cysentinel cimport sentinel_check, sentinel_check_exact
from builtins import sentinel
include "_sink.pxi"

# Sentinel construction is intentionally not benchmarked: it is alloc-dominated.
cpdef bint baseline_sentinel_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), sentinel)
        tb_sink_bint(r)
    return r

cpdef bint cypy_sentinel_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = sentinel_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef bint baseline_sentinel_check_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object o
    cdef bint r = False
    for k in range(n):
        o = tb_obj(p, k)
        r = type(o) is sentinel
        tb_sink_bint(r)
    return r

cpdef bint cypy_sentinel_check_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = sentinel_check_exact(tb_obj(p, k))
        tb_sink_bint(r)
    return r
