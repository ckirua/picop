# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cybuffer cimport buf_check
include "_sink.pxi"

cpdef bint baseline_buf_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), bytearray)
        tb_sink_bint(r)
    return r

cpdef bint cypy_buf_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = buf_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

