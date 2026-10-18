# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
"""Tier B loops: idiomatic typed Cython vs ``cypy.cytuple`` helpers."""

from cypy.cytuple cimport tuple_get, tuple_get_checked, tuple_len, tuple_size, tuple_check, tuple_check_exact

include "_sink.pxi"


cpdef object baseline_tget(tuple t, Py_ssize_t i, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = tb_tuple(t, k)[i]
        tb_sink_obj(r)
    return r


cpdef object cypy_tget(tuple t, Py_ssize_t i, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = tuple_get(tb_tuple(t, k), i)
        tb_sink_obj(r)
    return r


cpdef object baseline_tget_checked(tuple t, Py_ssize_t i, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = tb_tuple(t, k)[i]
        tb_sink_obj(r)
    return r


cpdef object cypy_tget_checked(tuple t, Py_ssize_t i, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = tuple_get_checked(tb_tuple(t, k), i)
        tb_sink_obj(r)
    return r


cpdef Py_ssize_t baseline_tlen(tuple t, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(tb_tuple(t, k))
        tb_sink_ssize(r)
    return r


cpdef Py_ssize_t cypy_tlen(tuple t, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = tuple_len(tb_tuple(t, k))
        tb_sink_ssize(r)
    return r


cpdef Py_ssize_t cypy_tsize(tuple t, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = tuple_size(tb_obj(t, k))
        tb_sink_ssize(r)
    return r


cpdef bint baseline_tcheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), tuple)
        tb_sink_bint(r)
    return r


cpdef bint cypy_tcheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = tuple_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r


cpdef bint baseline_tcheck_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = type(tb_obj(p, k)) is tuple
        tb_sink_bint(r)
    return r


cpdef bint cypy_tcheck_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = tuple_check_exact(tb_obj(p, k))
        tb_sink_bint(r)
    return r
