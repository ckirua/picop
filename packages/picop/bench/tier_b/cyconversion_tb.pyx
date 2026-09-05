# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from libc.stdlib cimport atof
from cypy.cyconversion cimport conv_cstr_to_double, conv_stricmp
include "_sink.pxi"

cpdef double baseline_conv_string_to_double(bytes s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef double r = 0.0
    cdef const char *p = s
    for k in range(n):
        tb_sink_ssize(k)
        r = atof(p)
        tb_sink_ssize(<Py_ssize_t>(r * 1000))
    return r

cpdef double cypy_conv_string_to_double(bytes s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef double r = 0.0
    cdef const char *p = s
    for k in range(n):
        r = conv_cstr_to_double(p)
        tb_sink_ssize(<Py_ssize_t>(r * 1000))
    return r

cpdef int baseline_conv_stricmp(bytes a, bytes b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    for k in range(n):
        tb_sink_ssize(k)
        r = 0 if (<bytes>tb_obj(a, k)).lower() == (<bytes>tb_obj(b, k)).lower() else 1
        tb_sink_ssize(r)
    return r

cpdef int cypy_conv_stricmp(bytes a, bytes b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int r = 0
    cdef const char *pa = a
    cdef const char *pb = b
    for k in range(n):
        tb_sink_ssize(k)
        r = conv_stricmp(pa, pb)
        tb_sink_ssize(r)
    return r
