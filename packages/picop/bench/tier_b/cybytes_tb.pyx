# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cybytes cimport bytes_contains, bytes_eq, bytes_len, bytes_check, bytes_check_exact
include "_sink.pxi"

cpdef bint baseline_bcontains(bytes haystack, bytes needle, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = needle in <bytes>tb_obj(haystack, k)
        tb_sink_bint(r)
    return r

cpdef bint cypy_bcontains(bytes haystack, bytes needle, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bytes_contains(<bytes>tb_obj(haystack, k), needle)
        tb_sink_bint(r)
    return r

cpdef bint baseline_beq(bytes a, bytes b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = <bytes>tb_obj(a, k) == b
        tb_sink_bint(r)
    return r

cpdef bint cypy_beq(bytes a, bytes b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bytes_eq(<bytes>tb_obj(a, k), b)
        tb_sink_bint(r)
    return r

cpdef Py_ssize_t baseline_blen(bytes b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(<bytes>tb_obj(b, k))
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_blen(bytes b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = bytes_len(<bytes>tb_obj(b, k))
        tb_sink_ssize(r)
    return r

cpdef bint baseline_bcheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), bytes)
        tb_sink_bint(r)
    return r

cpdef bint cypy_bcheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bytes_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef bint baseline_bcheck_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = type(tb_obj(p, k)) is bytes
        tb_sink_bint(r)
    return r

cpdef bint cypy_bcheck_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bytes_check_exact(tb_obj(p, k))
        tb_sink_bint(r)
    return r
