# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cyweakref cimport weakref_check
from weakref import ref
include "_sink.pxi"

cpdef bint baseline_weakref_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), ref)
        tb_sink_bint(r)
    return r

cpdef bint cypy_weakref_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = weakref_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

