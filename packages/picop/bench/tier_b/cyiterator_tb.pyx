# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cyiterator cimport iter_check
include "_sink.pxi"

cpdef bint baseline_iter_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = hasattr(tb_obj(p, k), "__next__")
        tb_sink_bint(r)
    return r

cpdef bint cypy_iter_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = iter_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

