# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cystr cimport str_cmp, str_lt, str_le, str_gt, str_ge, str_check, str_is
include "_sink.pxi"

cpdef int baseline_str_cmp(str a, str b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    for k in range(n):
        aa = <str>tb_obj(a, k)
        r = (aa > b) - (aa < b)
        tb_sink_ssize(r)
    return r

cpdef int cypy_str_cmp(str a, str b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    for k in range(n):
        r = str_cmp(<str>tb_obj(a, k), b)
        tb_sink_ssize(r)
    return r

cpdef bint baseline_str_lt(str a, str b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = <str>tb_obj(a, k) < b
        tb_sink_bint(r)
    return r

cpdef bint cypy_str_lt(str a, str b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = str_lt(<str>tb_obj(a, k), b)
        tb_sink_bint(r)
    return r

cpdef bint baseline_str_le(str a, str b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = <str>tb_obj(a, k) <= b
        tb_sink_bint(r)
    return r

cpdef bint cypy_str_le(str a, str b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = str_le(<str>tb_obj(a, k), b)
        tb_sink_bint(r)
    return r

cpdef bint baseline_str_gt(str a, str b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = <str>tb_obj(a, k) > b
        tb_sink_bint(r)
    return r

cpdef bint cypy_str_gt(str a, str b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = str_gt(<str>tb_obj(a, k), b)
        tb_sink_bint(r)
    return r

cpdef bint baseline_str_ge(str a, str b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = <str>tb_obj(a, k) >= b
        tb_sink_bint(r)
    return r

cpdef bint cypy_str_ge(str a, str b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = str_ge(<str>tb_obj(a, k), b)
        tb_sink_bint(r)
    return r

cpdef bint baseline_str_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), str)
        tb_sink_bint(r)
    return r

cpdef bint cypy_str_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = str_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef bint baseline_str_is(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = type(tb_obj(p, k)) is str
        tb_sink_bint(r)
    return r

cpdef bint cypy_str_is(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = str_is(tb_obj(p, k))
        tb_sink_bint(r)
    return r
