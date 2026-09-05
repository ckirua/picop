# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cycontextvars cimport ctx_check_exact
from contextvars import Context
include "_sink.pxi"

cpdef bint baseline_ctx_check_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = type(tb_obj(p, k)) is Context
        tb_sink_bint(r)
    return r

cpdef bint cypy_ctx_check_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = ctx_check_exact(tb_obj(p, k))
        tb_sink_bint(r)
    return r

