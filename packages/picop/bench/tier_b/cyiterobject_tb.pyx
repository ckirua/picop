# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cyiterobject cimport seqiter_check
include "_sink.pxi"

cpdef bint baseline_seqiter_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = type(tb_obj(p, k)).__name__ == "iterator"
        tb_sink_bint(r)
    return r

cpdef bint cypy_seqiter_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = seqiter_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

