# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cycode cimport code_check, code_name, code_firstlineno, code_argcount
include "_sink.pxi"

cpdef bint baseline_code_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), type(p))
        tb_sink_bint(r)
    return r

cpdef bint cypy_code_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = code_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef object baseline_code_name(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    cdef object c
    for k in range(n):
        c = tb_obj(p, k)
        r = (<object>c).co_name
        tb_sink_obj(r)
    return r

cpdef object cypy_code_name(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    cdef object c
    for k in range(n):
        c = tb_obj(p, k)
        r = code_name(c)
        tb_sink_obj(r)
    return r

cpdef int baseline_code_firstlineno(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    cdef object c
    for k in range(n):
        c = tb_obj(p, k)
        r = (<object>c).co_firstlineno
        tb_sink_ssize(r)
    return r

cpdef int cypy_code_firstlineno(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    cdef object c
    for k in range(n):
        c = tb_obj(p, k)
        r = code_firstlineno(c)
        tb_sink_ssize(r)
    return r

cpdef int baseline_code_argcount(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    cdef object c
    for k in range(n):
        c = tb_obj(p, k)
        r = (<object>c).co_argcount
        tb_sink_ssize(r)
    return r

cpdef int cypy_code_argcount(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    cdef object c
    for k in range(n):
        c = tb_obj(p, k)
        r = code_argcount(c)
        tb_sink_ssize(r)
    return r
