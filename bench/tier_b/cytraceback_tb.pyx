# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cytraceback cimport tb_check, tb_next, tb_frame, tb_lineno, tb_lasti, tb_depth
include "_sink.pxi"

cdef extern from "Python.h":
    ctypedef struct PyTracebackObject:
        PyObject *tb_next
        PyObject *tb_frame
        int tb_lasti
        int tb_lineno

cpdef bint baseline_tb_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), type(p))
        tb_sink_bint(r)
    return r

cpdef bint cypy_tb_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = tb_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef object baseline_tb_next(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r, t
    for k in range(n):
        t = tb_obj(p, k)
        r = t.tb_next
        tb_sink_obj(r)
    return r

cpdef object cypy_tb_next(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r, t
    for k in range(n):
        t = tb_obj(p, k)
        r = tb_next(t)
        tb_sink_obj(r)
    return r

cpdef object baseline_tb_frame(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r, t
    for k in range(n):
        t = tb_obj(p, k)
        r = t.tb_frame
        tb_sink_obj(r)
    return r

cpdef object cypy_tb_frame(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r, t
    for k in range(n):
        t = tb_obj(p, k)
        r = tb_frame(t)
        tb_sink_obj(r)
    return r

cpdef int baseline_tb_lineno(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    cdef object t
    for k in range(n):
        t = tb_obj(p, k)
        r = (<PyTracebackObject *>t).tb_lineno
        tb_sink_ssize(r)
    return r

cpdef int cypy_tb_lineno(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    cdef object t
    for k in range(n):
        t = tb_obj(p, k)
        r = tb_lineno(t)
        tb_sink_ssize(r)
    return r

cpdef int baseline_tb_lasti(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    cdef object t
    for k in range(n):
        t = tb_obj(p, k)
        r = (<PyTracebackObject *>t).tb_lasti
        tb_sink_ssize(r)
    return r

cpdef int cypy_tb_lasti(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    cdef object t
    for k in range(n):
        t = tb_obj(p, k)
        r = tb_lasti(t)
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t baseline_tb_depth(object p, Py_ssize_t n):
    cdef Py_ssize_t k, r = 0
    cdef object t
    cdef PyTracebackObject *cur
    for k in range(n):
        t = tb_obj(p, k)
        cur = <PyTracebackObject *>t
        r = 0
        while cur != NULL:
            r += 1
            cur = <PyTracebackObject *>cur.tb_next
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_tb_depth(object p, Py_ssize_t n):
    cdef Py_ssize_t k, r = 0
    cdef object t
    for k in range(n):
        t = tb_obj(p, k)
        r = tb_depth(t)
        tb_sink_ssize(r)
    return r
