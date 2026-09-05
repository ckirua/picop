# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cygc cimport gc_is_enabled
include "_sink.pxi"

cdef extern from "Python.h":
    int PyGC_IsEnabled() except -1

cpdef bint baseline_gc_is_enabled(Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        tb_sink_ssize(k)
        r = PyGC_IsEnabled() != 0
        tb_sink_bint(r)
    return r

cpdef bint cypy_gc_is_enabled(Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        tb_sink_ssize(k)
        r = gc_is_enabled()
        tb_sink_bint(r)
    return r

