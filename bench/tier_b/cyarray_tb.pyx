# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cpython.array cimport array
from cypy.cyarray cimport array_len, array_check
include "_sink.pxi"

cpdef Py_ssize_t baseline_aylen(array a, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(<array>tb_obj(a, k))
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_aylen(array a, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = array_len(<array>tb_obj(a, k))
        tb_sink_ssize(r)
    return r

cpdef bint baseline_aycheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), array)
        tb_sink_bint(r)
    return r

cpdef bint cypy_aycheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = array_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

