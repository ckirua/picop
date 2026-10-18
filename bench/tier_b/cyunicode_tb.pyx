# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cyunicode cimport uutf8_bytes, uintern, unicode_from_string, uintern_from_string, uutf8_eq
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


cpdef str smoke_unicode_from_string(bytes s):
    return unicode_from_string(s)


cpdef bint smoke_unicode_from_string_ok():
    cdef str a = unicode_from_string(b"hello")
    cdef str empty = unicode_from_string(b"")
    cdef str non_ascii = unicode_from_string(b"caf\xc3\xa9")
    cdef str interned = uintern_from_string(b"hello")
    if a != "hello" or empty != "" or non_ascii != "café":
        return False
    if interned != "hello":
        return False
    cdef str again = unicode_from_string(b"hello")
    return again == a


cpdef bint smoke_uutf8_eq_ok():
    if not uutf8_eq("hello", "hello"):
        return False
    if uutf8_eq("hello", "world"):
        return False
    if not uutf8_eq("", ""):
        return False
    if not uutf8_eq("café", "café"):
        return False
    if uutf8_eq("café", "cafe"):
        return False
    return True

