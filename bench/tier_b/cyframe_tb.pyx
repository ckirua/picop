# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cyframe cimport frame_check, frame_lineno, frame_code, frame_back
include "_sink.pxi"

cpdef bint baseline_frame_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), type(p))
        tb_sink_bint(r)
    return r

cpdef bint cypy_frame_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = frame_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef int baseline_frame_lineno(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    cdef object f
    for k in range(n):
        f = tb_obj(p, k)
        r = (<object>f).f_lineno
        tb_sink_ssize(r)
    return r

cpdef int cypy_frame_lineno(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    cdef object f
    for k in range(n):
        f = tb_obj(p, k)
        r = frame_lineno(f)
        tb_sink_ssize(r)
    return r

cpdef object baseline_frame_code(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    cdef object f
    for k in range(n):
        f = tb_obj(p, k)
        r = (<object>f).f_code
        tb_sink_obj(r)
    return r

cpdef object cypy_frame_code(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    cdef object f
    for k in range(n):
        f = tb_obj(p, k)
        r = frame_code(f)
        tb_sink_obj(r)
    return r

cpdef object baseline_frame_back(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    cdef object f
    for k in range(n):
        f = tb_obj(p, k)
        r = (<object>f).f_back
        tb_sink_obj(r)
    return r

cpdef object cypy_frame_back(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    cdef object f
    for k in range(n):
        f = tb_obj(p, k)
        r = frame_back(f)
        tb_sink_obj(r)
    return r
