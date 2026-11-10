# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cydescr cimport descr_is_data, descr_name, descr_objclass
include "_sink.pxi"

cpdef bint baseline_descr_is_data(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        d = tb_obj(p, k)
        r = hasattr(type(d), "__set__") or hasattr(type(d), "__delete__")
        tb_sink_bint(r)
    return r

cpdef bint cypy_descr_is_data(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = descr_is_data(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef object baseline_descr_name(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = tb_obj(p, k).__name__
        tb_sink_obj(r)
    return r

cpdef object cypy_descr_name(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = descr_name(tb_obj(p, k))
        tb_sink_obj(r)
    return r

cpdef object baseline_descr_objclass(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = tb_obj(p, k).__objclass__
        tb_sink_obj(r)
    return r

cpdef object cypy_descr_objclass(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = descr_objclass(tb_obj(p, k))
        tb_sink_obj(r)
    return r
