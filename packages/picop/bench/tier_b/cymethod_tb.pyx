# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cymethod cimport method_check
from types import MethodType
include "_sink.pxi"

cpdef bint baseline_method_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), MethodType)
        tb_sink_bint(r)
    return r

cpdef bint cypy_method_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = method_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

