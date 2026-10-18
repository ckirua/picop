# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cybool cimport bool_check
include "_sink.pxi"

cpdef bint baseline_bool_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), bool)
        tb_sink_bint(r)
    return r

cpdef bint cypy_bool_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bool_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

