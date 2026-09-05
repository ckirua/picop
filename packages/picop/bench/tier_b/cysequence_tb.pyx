# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cysequence cimport seq_get, seq_len
include "_sink.pxi"

cpdef object baseline_sqget(list l, Py_ssize_t i, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = (<list>tb_obj(l, k))[i]
        tb_sink_obj(r)
    return r

cpdef object cypy_sqget(list l, Py_ssize_t i, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = seq_get(tb_obj(l, k), i)
        tb_sink_obj(r)
    return r

cpdef Py_ssize_t baseline_sqlen(list l, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(<list>tb_obj(l, k))
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_sqlen(list l, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = seq_len(tb_obj(l, k))
        tb_sink_ssize(r)
    return r

