# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cylist cimport list_get, list_get_checked, list_len, list_check
include "_sink.pxi"

cpdef object baseline_lget(list l, Py_ssize_t i, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = (<list>tb_obj(l, k))[i]
        tb_sink_obj(r)
    return r

cpdef object cypy_lget(list l, Py_ssize_t i, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = list_get(<list>tb_obj(l, k), i)
        tb_sink_obj(r)
    return r

cpdef object cypy_lget_checked(list l, Py_ssize_t i, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = list_get_checked(<list>tb_obj(l, k), i)
        tb_sink_obj(r)
    return r

cpdef Py_ssize_t baseline_llen(list l, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(<list>tb_obj(l, k))
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_llen(list l, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = list_len(<list>tb_obj(l, k))
        tb_sink_ssize(r)
    return r

cpdef bint baseline_lcheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), list)
        tb_sink_bint(r)
    return r

cpdef bint cypy_lcheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = list_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

