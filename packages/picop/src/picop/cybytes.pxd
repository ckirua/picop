# cybytes.pxd
# Typed ``bytes`` helpers. Public docs live in ``cybytes.pyi``.
# Construction with uninit / C pointers / concat-resize: cdef.

from cpython.object cimport PyObject
from libc.stddef cimport size_t
from libc.string cimport memchr, memcmp

cdef extern from "string.h":
    void* memmem(const void *haystack, size_t haystacklen,
                 const void *needle, size_t needlelen) nogil

cdef extern from "Python.h":
    char* PyBytes_AS_STRING(object op) noexcept
    Py_ssize_t PyBytes_GET_SIZE(object op) noexcept
    bint PyBytes_Check(object o) noexcept
    bint PyBytes_CheckExact(object o) noexcept
    bytes PyBytes_FromString(const char *v)
    bytes PyBytes_FromStringAndSize(const char *v, Py_ssize_t len)
    bytes PyBytes_FromObject(object o)
    Py_ssize_t PyBytes_Size(object string) except -1
    char* PyBytes_AsString(object string) except NULL
    int PyBytes_AsStringAndSize(object obj, char **buffer, Py_ssize_t *length) except -1
    void PyBytes_Concat(PyObject **string, object newpart)
    void PyBytes_ConcatAndDel(PyObject **string, object newpart)
    int _PyBytes_Resize(PyObject **string, Py_ssize_t newsize) except -1
    bint PyByteArray_Check(object o) noexcept
    char* PyByteArray_AS_STRING(object bytearray) noexcept
    Py_ssize_t PyByteArray_GET_SIZE(object bytearray) noexcept


cdef inline bint bcheck(object p) noexcept:
    return PyBytes_Check(p)


cdef inline bint bcheck_exact(object p) noexcept:
    return PyBytes_CheckExact(p)


cdef inline char* bas_string(bytes b) noexcept:
    # Borrowed internal buffer; do not mutate or outlive b.
    return PyBytes_AS_STRING(b)


cdef inline char* bas_string_checked(object b) except NULL:
    return PyBytes_AsString(b)


cdef inline Py_ssize_t blen(bytes b) noexcept:
    return PyBytes_GET_SIZE(b)


cdef inline Py_ssize_t bsize(object b) except -1:
    return PyBytes_Size(b)


cdef inline bint bcontains(bytes haystack, bytes needle) noexcept:
    # memchr/memmem win on small buffers; CPython stringlib wins past ~256B.
    cdef Py_ssize_t hlen = PyBytes_GET_SIZE(haystack)
    cdef Py_ssize_t nlen = PyBytes_GET_SIZE(needle)
    if nlen == 0:
        return True
    if nlen > hlen:
        return False
    if hlen > 256:
        return needle in haystack
    cdef char *hp = PyBytes_AS_STRING(haystack)
    cdef char *np = PyBytes_AS_STRING(needle)
    if nlen == 1:
        return memchr(hp, <unsigned char>np[0], <size_t>hlen) is not NULL
    return memmem(hp, <size_t>hlen, np, <size_t>nlen) is not NULL


cdef inline bint beq(bytes a, bytes b) noexcept:
    # Identity / len short-circuit + memcmp on typed bytes (mirror streq).
    if a is b:
        return True
    cdef Py_ssize_t la = PyBytes_GET_SIZE(a)
    if la != PyBytes_GET_SIZE(b):
        return False
    if la == 0:
        return True
    return memcmp(PyBytes_AS_STRING(a), PyBytes_AS_STRING(b), <size_t>la) == 0


cdef inline bint bne(bytes a, bytes b) noexcept:
    return not beq(a, b)


cdef inline bint bba_eq(object a, object b) noexcept:
    # Content eq for ``bytes``/``bytearray`` either order (and same-type).
    # Prefer typed ``bytes_eq`` / ``bytearray_eq`` for known same-type hot paths.
    # Distinct from ``buf_eq`` (buffer-protocol / memoryview path).
    if a is b:
        return True
    cdef char *pa
    cdef char *pb
    cdef Py_ssize_t la, lb

    if PyBytes_Check(a):
        pa = PyBytes_AS_STRING(a)
        la = PyBytes_GET_SIZE(a)
    elif PyByteArray_Check(a):
        pa = PyByteArray_AS_STRING(a)
        la = PyByteArray_GET_SIZE(a)
    else:
        return False

    if PyBytes_Check(b):
        pb = PyBytes_AS_STRING(b)
        lb = PyBytes_GET_SIZE(b)
    elif PyByteArray_Check(b):
        pb = PyByteArray_AS_STRING(b)
        lb = PyByteArray_GET_SIZE(b)
    else:
        return False

    if la != lb:
        return False
    if la == 0:
        return True
    return memcmp(pa, pb, <size_t>la) == 0


cdef inline bint bstartswith(bytes s, bytes prefix) noexcept:
    cdef Py_ssize_t sn = PyBytes_GET_SIZE(s)
    cdef Py_ssize_t pn = PyBytes_GET_SIZE(prefix)
    if pn == 0:
        return True
    if pn > sn:
        return False
    return memcmp(PyBytes_AS_STRING(s), PyBytes_AS_STRING(prefix), <size_t>pn) == 0


cdef inline bint bendswith(bytes s, bytes suffix) noexcept:
    cdef Py_ssize_t sn = PyBytes_GET_SIZE(s)
    cdef Py_ssize_t pn = PyBytes_GET_SIZE(suffix)
    if pn == 0:
        return True
    if pn > sn:
        return False
    return memcmp(PyBytes_AS_STRING(s) + (sn - pn), PyBytes_AS_STRING(suffix), <size_t>pn) == 0


cdef inline bytes bfrom_object(object o):
    return PyBytes_FromObject(o)


cdef inline bytes bfrom_string(const char *v):
    return PyBytes_FromString(v)


cdef inline bytes bfrom_string_and_size(const char *v, Py_ssize_t n):
    return PyBytes_FromStringAndSize(v, n)


cdef inline bytes bnew(Py_ssize_t n):
    # Uninitialized — fill before Python exposure (unlike zeroed bytes(n)).
    return PyBytes_FromStringAndSize(NULL, n)


cdef inline bytes bconcat(bytes left, object newpart):
    # Steals/owns ref at *left; if shared, Concat allocates a new object.
    cdef PyObject *p = <PyObject*>left
    PyBytes_Concat(&p, newpart)
    if p is NULL:
        return None
    return <bytes>p


cdef inline bytes bconcat_and_del(bytes left, object newpart):
    # Concat + DECREF newpart (PyBytes_ConcatAndDel).
    cdef PyObject *p = <PyObject*>left
    PyBytes_ConcatAndDel(&p, newpart)
    if p is NULL:
        return None
    return <bytes>p


cdef inline bytes bresize(bytes b, Py_ssize_t newsize):
    # Caller must own the ref passed in. Non-unique → copy-out (not SystemError).
    cdef PyObject *p = <PyObject*>b
    cdef int rc = _PyBytes_Resize(&p, newsize)
    if rc < 0 or p is NULL:
        return None
    return <bytes>p

# Wave 4 N1/N5 preferred names (0.3: soft letter/bare are cdef-only)

cpdef inline bint bytes_check(object p) noexcept:
    return bcheck(p)

cpdef inline bint bytes_check_exact(object p) noexcept:
    return bcheck_exact(p)

cdef inline bytes bytes_concat(bytes left, object newpart):
    return bconcat(left, newpart)

cdef inline bytes bytes_concat_and_del(bytes left, object newpart):
    return bconcat_and_del(left, newpart)

cpdef inline bint bytes_contains(bytes haystack, bytes needle) noexcept:
    return bcontains(haystack, needle)

cpdef inline bint bytes_eq(bytes a, bytes b) noexcept:
    return beq(a, b)

cpdef inline bint bytes_bytearray_eq(object a, object b) noexcept:
    return bba_eq(a, b)

cpdef inline bint bytes_ne(bytes a, bytes b) noexcept:
    return bne(a, b)

cpdef inline bint bytes_startswith(bytes s, bytes prefix) noexcept:
    return bstartswith(s, prefix)

cpdef inline bint bytes_endswith(bytes s, bytes suffix) noexcept:
    return bendswith(s, suffix)

cpdef inline bytes bytes_from_object(object o):
    return bfrom_object(o)

cdef inline bytes bytes_from_string(const char *v):
    return bfrom_string(v)

cdef inline bytes bytes_from_string_and_size(const char *v, Py_ssize_t n):
    return bfrom_string_and_size(v, n)

cpdef inline Py_ssize_t bytes_len(bytes b) noexcept:
    return blen(b)

cdef inline bytes bytes_new(Py_ssize_t n):
    return bnew(n)

cdef inline bytes bytes_resize(bytes b, Py_ssize_t newsize):
    return bresize(b, newsize)

cpdef inline Py_ssize_t bytes_size(object b) except -1:
    return bsize(b)

