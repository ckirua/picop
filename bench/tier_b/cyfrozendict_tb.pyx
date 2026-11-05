# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cyfrozendict cimport (
    frozendict_check,
    frozendict_check_exact,
    anydict_check,
    anydict_check_exact,
    anydict_len,
)
include "_sink.pxi"

cpdef bint baseline_frozendict_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), frozendict)
        tb_sink_bint(r)
    return r

cpdef bint cypy_frozendict_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = frozendict_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef bint baseline_frozendict_check_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object o
    cdef bint r = False
    for k in range(n):
        o = tb_obj(p, k)
        r = type(o) is frozendict
        tb_sink_bint(r)
    return r

cpdef bint cypy_frozendict_check_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = frozendict_check_exact(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef bint baseline_anydict_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), (dict, frozendict))
        tb_sink_bint(r)
    return r

cpdef bint cypy_anydict_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = anydict_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef bint baseline_anydict_check_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object o
    cdef bint r = False
    for k in range(n):
        o = tb_obj(p, k)
        r = type(o) is dict or type(o) is frozendict
        tb_sink_bint(r)
    return r

cpdef bint cypy_anydict_check_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = anydict_check_exact(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef Py_ssize_t baseline_anydict_len(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(tb_obj(p, k))
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_anydict_len(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = anydict_len(tb_obj(p, k))
        tb_sink_ssize(r)
    return r
