# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cybytearray cimport bytearray_len, bytearray_check, bytearray_check_exact
include "_sink.pxi"

cpdef Py_ssize_t baseline_balen(bytearray ba, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(<bytearray>tb_obj(ba, k))
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_balen(bytearray ba, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = bytearray_len(<bytearray>tb_obj(ba, k))
        tb_sink_ssize(r)
    return r

cpdef bint baseline_bacheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), bytearray)
        tb_sink_bint(r)
    return r

cpdef bint cypy_bacheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bytearray_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef bint baseline_bacheck_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = type(tb_obj(p, k)) is bytearray
        tb_sink_bint(r)
    return r

cpdef bint cypy_bacheck_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bytearray_check_exact(tb_obj(p, k))
        tb_sink_bint(r)
    return r

