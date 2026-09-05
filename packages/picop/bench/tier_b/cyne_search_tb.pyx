# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cpython.array cimport array
from cypy.cybytes cimport bytes_ne, bytes_startswith, bytes_endswith
from cypy.cybytearray cimport bytearray_ne, bytearray_contains
from cypy.cyarray cimport array_ne
from cypy.cymemoryview cimport memoryview_ne
include "_sink.pxi"

cpdef bint baseline_bytes_ne(bytes a, bytes b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = <bytes>tb_obj(a, k) != b
        tb_sink_bint(r)
    return r

cpdef bint cypy_bytes_ne(bytes a, bytes b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bytes_ne(<bytes>tb_obj(a, k), b)
        tb_sink_bint(r)
    return r

cpdef bint baseline_bytes_startswith(bytes s, bytes prefix, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = (<bytes>tb_obj(s, k)).startswith(prefix)
        tb_sink_bint(r)
    return r

cpdef bint cypy_bytes_startswith(bytes s, bytes prefix, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bytes_startswith(<bytes>tb_obj(s, k), prefix)
        tb_sink_bint(r)
    return r

cpdef bint baseline_bytes_endswith(bytes s, bytes suffix, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = (<bytes>tb_obj(s, k)).endswith(suffix)
        tb_sink_bint(r)
    return r

cpdef bint cypy_bytes_endswith(bytes s, bytes suffix, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bytes_endswith(<bytes>tb_obj(s, k), suffix)
        tb_sink_bint(r)
    return r

cpdef bint baseline_bytearray_ne(bytearray a, bytearray b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = <bytearray>tb_obj(a, k) != b
        tb_sink_bint(r)
    return r

cpdef bint cypy_bytearray_ne(bytearray a, bytearray b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bytearray_ne(<bytearray>tb_obj(a, k), b)
        tb_sink_bint(r)
    return r

cpdef bint baseline_bytearray_contains(bytearray haystack, bytes needle, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = needle in <bytearray>tb_obj(haystack, k)
        tb_sink_bint(r)
    return r

cpdef bint cypy_bytearray_contains(bytearray haystack, bytes needle, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bytearray_contains(<bytearray>tb_obj(haystack, k), needle)
        tb_sink_bint(r)
    return r

cpdef bint baseline_array_ne(array a, array b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = <array>tb_obj(a, k) != b
        tb_sink_bint(r)
    return r

cpdef bint cypy_array_ne(array a, array b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = array_ne(<array>tb_obj(a, k), b)
        tb_sink_bint(r)
    return r

cpdef bint baseline_memoryview_ne(memoryview a, memoryview b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = <memoryview>tb_obj(a, k) != b
        tb_sink_bint(r)
    return r

cpdef bint cypy_memoryview_ne(memoryview a, memoryview b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = memoryview_ne(<memoryview>tb_obj(a, k), b)
        tb_sink_bint(r)
    return r
