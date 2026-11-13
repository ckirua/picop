# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
"""Tier B loops: idiomatic typed Cython vs ``picop.cytuple`` helpers."""

from picop.cytuple cimport tuple_get, tuple_get_checked, tuple_len, tuple_size, tuple_check, tuple_check_exact, tuple_from_array, tuple_new, tuple_set

import sys

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
cpdef object smoke_from_array(tuple t):
    # Correctness smoke: array of borrowed refs -> tuple with one INCREF each.
    cdef PyObject *arr[4]
    arr[0] = <PyObject*>t[0]
    arr[1] = <PyObject*>t[1]
    arr[2] = <PyObject*>t[2]
    arr[3] = <PyObject*>t[3]
    return tuple_from_array(arr, 4)


cpdef object smoke_refcount():
    # tuple_from_array INCREFs each element exactly once and releases it when
    # the tuple dies; size 0 yields (); negative size raises ValueError.
    cdef PyObject *arr[3]
    cdef object o1 = object()
    cdef object o2 = object()
    cdef object o3 = object()
    cdef Py_ssize_t rc0 = sys.getrefcount(o1)
    arr[0] = <PyObject*>o1
    arr[1] = <PyObject*>o2
    arr[2] = <PyObject*>o3
    cdef tuple t = tuple_from_array(arr, 3)
    cdef Py_ssize_t rc1 = sys.getrefcount(o1)
    cdef tuple t0 = tuple_from_array(arr, 0)
    del t
    cdef Py_ssize_t rc2 = sys.getrefcount(o1)
    cdef str err = ""
    try:
        tuple_from_array(arr, -1)
    except ValueError as exc:
        err = str(exc)
    return (rc1 == rc0 + 1, rc2 == rc0, len(t0) == 0, err)


cpdef object cypy_tfrom_array(tuple t, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    cdef PyObject *arr[4]
    for k in range(n):
        r = tb_tuple(t, k)
        arr[0] = <PyObject*>r[0]
        arr[1] = <PyObject*>r[1]
        arr[2] = <PyObject*>r[2]
        arr[3] = <PyObject*>r[3]
        r = tuple_from_array(arr, 4)
        tb_sink_obj(r)
    return r
cpdef object baseline_tfrom_literal(tuple t, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = tb_tuple(t, k)
        r = (r[0], r[1], r[2], r[3])
        tb_sink_obj(r)
    return r
cpdef object baseline_tnew_fill(tuple t, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    cdef object src
    for k in range(n):
        src = tb_tuple(t, k)
        r = tuple_new(4)
        tuple_set(r, 0, src[0])
        tuple_set(r, 1, src[1])
        tuple_set(r, 2, src[2])
        tuple_set(r, 3, src[3])
        tb_sink_obj(r)
    return r
