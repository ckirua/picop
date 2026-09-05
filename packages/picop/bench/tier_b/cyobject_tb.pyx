# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cyobject cimport obj_type, obj_len
include "_sink.pxi"

cpdef object baseline_obj_type(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = type(tb_obj(p, k))
        tb_sink_obj(r)
    return r

cpdef object cypy_obj_type(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = obj_type(tb_obj(p, k))
        tb_sink_obj(r)
    return r

cpdef Py_ssize_t baseline_obj_len(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(tb_obj(p, k))
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_obj_len(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = obj_len(tb_obj(p, k))
        tb_sink_ssize(r)
    return r

