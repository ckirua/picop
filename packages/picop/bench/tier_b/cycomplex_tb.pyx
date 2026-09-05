# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cycomplex cimport complex_check
include "_sink.pxi"

cpdef bint baseline_complex_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), complex)
        tb_sink_bint(r)
    return r

cpdef bint cypy_complex_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = complex_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

