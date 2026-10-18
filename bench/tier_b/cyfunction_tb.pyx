# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cyfunction cimport func_check
from types import FunctionType
include "_sink.pxi"

cpdef bint baseline_func_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), FunctionType)
        tb_sink_bint(r)
    return r

cpdef bint cypy_func_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = func_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

