# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cysys cimport sys_get_attr, sys_get_attr_string, sys_get_object, sys_get_xoptions
include "_sink.pxi"

cpdef Py_ssize_t baseline_get_object(object name, Py_ssize_t n):
    cdef Py_ssize_t i
    cdef object value
    cdef object system = __import__("sys")
    for i in range(n):
        value = getattr(system, name)
        tb_sink_obj(value)
    return n

cpdef Py_ssize_t cypy_get_object(object name, Py_ssize_t n):
    cdef Py_ssize_t i
    cdef object value
    for i in range(n):
        value = sys_get_object(name)
        tb_sink_obj(value)
    return n

cpdef Py_ssize_t baseline_get_xoptions(Py_ssize_t n):
    cdef Py_ssize_t i
    cdef object value
    cdef object system = __import__("sys")
    for i in range(n):
        value = system._xoptions
        tb_sink_obj(value)
    return n

cpdef Py_ssize_t cypy_get_xoptions(Py_ssize_t n):
    cdef Py_ssize_t i
    cdef object value
    for i in range(n):
        value = sys_get_xoptions()
        tb_sink_obj(value)
    return n

cpdef Py_ssize_t baseline_get_attr(object name, Py_ssize_t n):
    cdef Py_ssize_t i
    cdef object value
    cdef object system = __import__("sys")
    for i in range(n):
        value = getattr(system, name)
        tb_sink_obj(value)
    return n

cpdef Py_ssize_t cypy_get_attr(object name, Py_ssize_t n):
    cdef Py_ssize_t i
    cdef object value
    for i in range(n):
        value = sys_get_attr(name)
        tb_sink_obj(value)
    return n

cpdef Py_ssize_t baseline_get_attr_string(object name, Py_ssize_t n):
    cdef Py_ssize_t i
    cdef object value
    cdef object system = __import__("sys")
    for i in range(n):
        value = getattr(system, name)
        tb_sink_obj(value)
    return n

cpdef Py_ssize_t cypy_get_attr_string(object name, Py_ssize_t n):
    cdef Py_ssize_t i
    cdef object value
    for i in range(n):
        value = sys_get_attr_string(name)
        tb_sink_obj(value)
    return n
