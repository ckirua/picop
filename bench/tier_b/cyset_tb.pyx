# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cyset cimport set_contains, set_len, set_check
include "_sink.pxi"

cpdef bint baseline_scontains(object s, object value, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = value in tb_obj(s, k)
        tb_sink_bint(r)
    return r

cpdef bint cypy_scontains(object s, object value, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = set_contains(tb_obj(s, k), value)
        tb_sink_bint(r)
    return r

cpdef Py_ssize_t baseline_slen(set s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(<set>tb_obj(s, k))
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_slen(set s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = set_len(<set>tb_obj(s, k))
        tb_sink_ssize(r)
    return r

cpdef bint baseline_scheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), set)
        tb_sink_bint(r)
    return r

cpdef bint cypy_scheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = set_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

