# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cyunicode cimport uutf8_bytes, uintern
from cpython.object cimport PyObject
include "_sink.pxi"

cdef extern from "Python.h":
    object PyUnicode_AsUTF8String(object unicode)
    void PyUnicode_InternInPlace(PyObject **)

cpdef bytes baseline_uutf8_bytes(str s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bytes r
    for k in range(n):
        r = <bytes>PyUnicode_AsUTF8String(<str>tb_obj(s, k))
        tb_sink_obj(r)
    return r

cpdef bytes cypy_uutf8_bytes(str s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bytes r
    for k in range(n):
        r = uutf8_bytes(<str>tb_obj(s, k))
        tb_sink_obj(r)
    return r

cpdef str baseline_uintern(str s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef PyObject *p
    cdef str r
    for k in range(n):
        r = <str>tb_obj(s, k)
        p = <PyObject*>r
        PyUnicode_InternInPlace(&p)
        r = <str>p
        tb_sink_obj(r)
    return r

cpdef str cypy_uintern(str s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef str r
    for k in range(n):
        r = uintern(<str>tb_obj(s, k))
        tb_sink_obj(r)
    return r
