# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cytype cimport type_check, type_get_flags, type_get_name, type_get_qualname, type_get_dict
from picop.cytype cimport PyType_GetFlags
include "_sink.pxi"

cpdef bint baseline_type_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), type)
        tb_sink_bint(r)
    return r

cpdef bint cypy_type_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = type_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef object baseline_type_get_name(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = (<type>p).__name__
        tb_sink_obj(r)
    return r

cpdef object cypy_type_get_name(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = type_get_name(p)
        tb_sink_obj(r)
    return r

cpdef object baseline_type_get_qualname(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = (<type>p).__qualname__
        tb_sink_obj(r)
    return r

cpdef object cypy_type_get_qualname(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = type_get_qualname(p)
        tb_sink_obj(r)
    return r

cpdef unsigned long baseline_type_get_flags(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef unsigned long r = 0
    for k in range(n):
        r = PyType_GetFlags(<type>p)
        tb_sink_ssize(<Py_ssize_t>r)
    return r

cpdef unsigned long cypy_type_get_flags(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef unsigned long r = 0
    for k in range(n):
        r = type_get_flags(p)
        tb_sink_ssize(<Py_ssize_t>r)
    return r

cpdef object baseline_type_get_dict(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = (<type>p).__dict__
        tb_sink_obj(r)
    return r

cpdef object cypy_type_get_dict(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = None
    for k in range(n):
        r = type_get_dict(p)
        tb_sink_obj(r)
    return r

