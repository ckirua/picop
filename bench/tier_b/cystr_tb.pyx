# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cystr cimport str_contains, str_eq, str_len, str_check_exact
include "_sink.pxi"

cpdef bint baseline_contains(str haystack, str needle, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = needle in <str>tb_obj(haystack, k)
        tb_sink_bint(r)
    return r

cpdef bint cypy_contains(str haystack, str needle, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = str_contains(<str>tb_obj(haystack, k), needle)
        tb_sink_bint(r)
    return r

cpdef bint baseline_streq(str a, str b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = <str>tb_obj(a, k) == b
        tb_sink_bint(r)
    return r

cpdef bint cypy_streq(str a, str b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = str_eq(<str>tb_obj(a, k), b)
        tb_sink_bint(r)
    return r

cpdef Py_ssize_t baseline_strlen(str s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(<str>tb_obj(s, k))
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_strlen(str s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = str_len(<str>tb_obj(s, k))
        tb_sink_ssize(r)
    return r

cpdef bint baseline_is_str(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = type(tb_obj(p, k)) is str
        tb_sink_bint(r)
    return r

cpdef bint cypy_is_str(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = str_check_exact(tb_obj(p, k))
        tb_sink_bint(r)
    return r

