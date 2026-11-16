# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cylong cimport long_check, long_as_int32, long_as_uint32, long_as_long
include "_sink.pxi"

cpdef bint baseline_long_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), int)
        tb_sink_bint(r)
    return r

cpdef bint cypy_long_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = long_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r


cpdef int baseline_long_as_int32(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    for k in range(n):
        r = <int>int(tb_obj(p, k))
        tb_sink_ssize(r)
    return r

cpdef int cypy_long_as_int32(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    for k in range(n):
        r = long_as_int32(tb_obj(p, k))
        tb_sink_ssize(r)
    return r

cpdef bint depth_probes():
    cdef bint caught
    cdef object value
    caught = False
    try:
        long_as_int32(2**32)
    except OverflowError:
        caught = True
    assert caught
    try:
        long_as_uint32(-1)
    except ValueError:
        caught = True
    assert caught
    assert long_as_int32(True) == 1
    caught = False
    try:
        long_as_int32("not an int")
    except TypeError:
        caught = True
    assert caught
    value = 42
    assert long_as_int32(value) == long_as_long(value)
    return True
