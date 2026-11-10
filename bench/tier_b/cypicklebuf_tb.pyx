# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cypicklebuf cimport pickle_buffer_from_object
include "_sink.pxi"

cpdef Py_ssize_t baseline_from_object(object obj, Py_ssize_t n):
    cdef Py_ssize_t i
    cdef object value
    for i in range(n):
        value = memoryview(obj)
        tb_sink_obj(value)
    return n

cpdef Py_ssize_t cypy_from_object(object obj, Py_ssize_t n):
    cdef Py_ssize_t i
    cdef object value
    for i in range(n):
        value = pickle_buffer_from_object(obj)
        tb_sink_obj(value)
    return n
