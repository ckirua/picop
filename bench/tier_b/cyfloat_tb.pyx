# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cyfloat cimport float_check
include "_sink.pxi"

cpdef bint baseline_float_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), float)
        tb_sink_bint(r)
    return r

cpdef bint cypy_float_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = float_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

from picop.cyfloat cimport float_pack8, float_unpack8
import struct

cpdef object baseline_struct_pack(double x, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = b""
    for k in range(n):
        r = struct.pack("<d", x)
        tb_sink_obj(r)
    return r

cpdef object cypy_float_pack8(double x, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r = b""
    for k in range(n):
        r = float_pack8(x)
        tb_sink_obj(r)
    return r

cpdef double baseline_struct_unpack(object b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef double r = 0
    for k in range(n):
        r = struct.unpack("<d", b)[0]
        tb_sink_ssize(<Py_ssize_t>r)
    return r

cpdef double cypy_float_unpack8(object b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef double r = 0
    for k in range(n):
        r = float_unpack8(b)
        tb_sink_ssize(<Py_ssize_t>r)
    return r

