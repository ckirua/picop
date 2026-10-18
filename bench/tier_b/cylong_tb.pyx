# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cylong cimport long_check
include "_sink.pxi"

cpdef bint baseline_long_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), int)
        tb_sink_bint(r)
    return r

cpdef bint cypy_long_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = long_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

