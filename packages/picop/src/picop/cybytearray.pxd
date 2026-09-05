# cybytearray.pxd
# Typed ``bytearray`` helpers. Public docs live in ``cybytearray.pyi``.
# C pointers / uninit construction: cdef.

from cpython.object cimport PyObject
from libc.stddef cimport size_t
from libc.string cimport memchr, memcmp

cdef extern from "string.h":
    void* memmem(const void *haystack, size_t haystacklen,
                 const void *needle, size_t needlelen) nogil


cdef extern from "Python.h":
    bint PyByteArray_Check(object o) noexcept
    bint PyByteArray_CheckExact(object o) noexcept
    bytearray PyByteArray_FromObject(object o)
    bytearray PyByteArray_FromStringAndSize(const char *string, Py_ssize_t len)
    bytearray PyByteArray_Concat(object a, object b)
    Py_ssize_t PyByteArray_Size(object bytearray) except -1
    char* PyByteArray_AsString(object bytearray) except NULL
    int PyByteArray_Resize(object bytearray, Py_ssize_t len) except -1
    char* PyByteArray_AS_STRING(object bytearray) noexcept
    Py_ssize_t PyByteArray_GET_SIZE(object bytearray) noexcept
    char* PyBytes_AS_STRING(object op) noexcept
    Py_ssize_t PyBytes_GET_SIZE(object op) noexcept


cdef inline bint bacheck(object p) noexcept:
    return PyByteArray_Check(p)


cdef inline bint bacheck_exact(object p) noexcept:
    return PyByteArray_CheckExact(p)


cdef inline Py_ssize_t balen(bytearray ba) noexcept:
    return PyByteArray_GET_SIZE(ba)


cdef inline Py_ssize_t basize(object ba) except -1:
    return PyByteArray_Size(ba)


cdef inline bytearray bafrom_object(object o):
    return PyByteArray_FromObject(o)


cdef inline bytearray baconcat(object a, object b):
    return PyByteArray_Concat(a, b)


cdef inline char* baas_string(bytearray ba) noexcept:
    # Borrowed mutable buffer; do not outlive ba.
    return PyByteArray_AS_STRING(ba)


cdef inline char* baas_string_checked(object ba) except NULL:
    return PyByteArray_AsString(ba)


cdef inline bytearray bafrom_string_and_size(const char *string, Py_ssize_t n):
    return PyByteArray_FromStringAndSize(string, n)


cdef inline bytearray banew(Py_ssize_t n):
    # Uninitialized — fill before Python exposure (unlike zeroed bytearray(n)).
    return PyByteArray_FromStringAndSize(NULL, n)


cdef inline int baresize(bytearray ba, Py_ssize_t n) except -1:
    return PyByteArray_Resize(ba, n)


cdef inline bint baeq(bytearray a, bytearray b) noexcept:
    # Identity / len short-circuit + memcmp on typed bytearray (mirror beq).
    if a is b:
        return True
    cdef Py_ssize_t la = PyByteArray_GET_SIZE(a)
    if la != PyByteArray_GET_SIZE(b):
        return False
    if la == 0:
        return True
    return memcmp(PyByteArray_AS_STRING(a), PyByteArray_AS_STRING(b), <size_t>la) == 0


cdef inline bint bane(bytearray a, bytearray b) noexcept:
    return not baeq(a, b)


cdef inline bint bacontains(bytearray haystack, bytes needle) noexcept:
    # memchr/memmem win on small buffers; CPython stringlib wins past ~256B.
    cdef Py_ssize_t hlen = PyByteArray_GET_SIZE(haystack)
    cdef Py_ssize_t nlen = PyBytes_GET_SIZE(needle)
    if nlen == 0:
        return True
    if nlen > hlen:
        return False
    if hlen > 256:
        return needle in haystack
    cdef char *hp = PyByteArray_AS_STRING(haystack)
    cdef char *np = PyBytes_AS_STRING(needle)
    if nlen == 1:
        return memchr(hp, <unsigned char>np[0], <size_t>hlen) is not NULL
    return memmem(hp, <size_t>hlen, np, <size_t>nlen) is not NULL

# Wave 4 N1/N5 preferred names (0.3: soft letter/bare are cdef-only)

cdef inline char* bytearray_as_string(bytearray ba) noexcept:
    return baas_string(ba)

cdef inline char* bytearray_as_string_checked(object ba) except NULL:
    return baas_string_checked(ba)

cpdef inline bint bytearray_check(object p) noexcept:
    return bacheck(p)

cpdef inline bint bytearray_check_exact(object p) noexcept:
    return bacheck_exact(p)

cpdef inline bytearray bytearray_concat(object a, object b):
    return baconcat(a, b)

cpdef inline bytearray bytearray_from_object(object o):
    return bafrom_object(o)

cdef inline bytearray bytearray_from_string_and_size(const char *string, Py_ssize_t n):
    return bafrom_string_and_size(string, n)

cpdef inline Py_ssize_t bytearray_len(bytearray ba) noexcept:
    return balen(ba)

cpdef inline bint bytearray_eq(bytearray a, bytearray b) noexcept:
    return baeq(a, b)

cpdef inline bint bytearray_ne(bytearray a, bytearray b) noexcept:
    return bane(a, b)

cpdef inline bint bytearray_contains(bytearray haystack, bytes needle) noexcept:
    return bacontains(haystack, needle)

cdef inline bytearray bytearray_new(Py_ssize_t n):
    return banew(n)

cpdef inline int bytearray_resize(bytearray ba, Py_ssize_t n) except -1:
    return baresize(ba, n)

cpdef inline Py_ssize_t bytearray_size(object ba) except -1:
    return basize(ba)

