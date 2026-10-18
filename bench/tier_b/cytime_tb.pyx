# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cytime cimport time_wall
include "_sink.pxi"

cdef extern from "Python.h":
    double PyFloat_AsDouble(object) except? -1.0

cpdef double baseline_time_time(Py_ssize_t n):
    cdef Py_ssize_t k
    cdef double r = 0.0
    cdef object mod
    import time as _time
    fn = _time.time
    for k in range(n):
        tb_sink_ssize(k)
        r = fn()
        tb_sink_ssize(<Py_ssize_t>(r * 1000))
    return r

cpdef double cypy_time_time(Py_ssize_t n):
    cdef Py_ssize_t k
    cdef double r = 0.0
    for k in range(n):
        tb_sink_ssize(k)
        r = time_wall()
        tb_sink_ssize(<Py_ssize_t>(r * 1000))
    return r

