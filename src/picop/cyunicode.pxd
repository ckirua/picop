# cyunicode.pxd
# UTF-8 borrow / owning bytes + intern slice of ``cpython.unicode``.
# High-level str helpers: ``cystr``. Public docs: ``cyunicode.pyi``.
# ``uutf8*`` borrowed pointers must not outlive ``s``.

from cpython.object cimport PyObject
from libc.stddef cimport size_t
from libc.string cimport memcmp
from .cystr cimport str_eq
from cpython.unicode cimport (
    PyUnicode_AsUTF8,
    PyUnicode_AsUTF8AndSize,
    PyUnicode_AsUTF8String,
    PyUnicode_FromString,
    PyUnicode_InternFromString,
)


cdef extern from "Python.h":
    ctypedef struct PyUnicodeWriter:
        pass
    PyUnicodeWriter *PyUnicodeWriter_Create(Py_ssize_t length)
    void PyUnicodeWriter_Discard(PyUnicodeWriter *writer)
    str PyUnicodeWriter_Finish(PyUnicodeWriter *writer)
    int PyUnicodeWriter_WriteStr(PyUnicodeWriter *writer, object text) except -1
    int PyUnicodeWriter_WriteChar(PyUnicodeWriter *writer, Py_UCS4 ch) except -1
    int PyUnicodeWriter_WriteASCII(PyUnicodeWriter *writer, const char *text, Py_ssize_t size) except -1
    int PyUnicodeWriter_WriteRepr(PyUnicodeWriter *writer, object obj) except -1
    int PyUnicodeWriter_WriteSubstring(PyUnicodeWriter *writer, str text, Py_ssize_t start, Py_ssize_t end) except -1
    int PyUnicodeWriter_WriteUTF8(PyUnicodeWriter *writer, const char *utf8, Py_ssize_t size) except -1
    void PyUnicode_InternInPlace(PyObject **string)

cdef class UnicodeWriter:
    cdef PyUnicodeWriter *_w
    cdef void _check_open(self) except *
    cpdef write(self, object text)
    cpdef write_char(self, Py_UCS4 ch)
    cpdef write_ascii(self, str text)
    cpdef write_repr(self, object obj)
    cpdef write_substring(self, str text, Py_ssize_t start=*, Py_ssize_t end=*)
    cpdef write_utf8(self, bytes data)
    cpdef str finish(self)
    cpdef discard(self)


cdef inline const char *uutf8(str s) except NULL:
    # Borrowed UTF-8; NUL-terminated; do not outlive ``s``.
    return PyUnicode_AsUTF8(s)


cdef inline const char *uutf8_and_size(str s, Py_ssize_t *size) except NULL:
    # Borrowed UTF-8 + byte length.
    return PyUnicode_AsUTF8AndSize(s, size)


cdef inline bint uutf8_eq(str a, str b) except -1:
    # Compare UTF-8 byte views (embedded NUL OK via size). Pointers must not outlive ``a``/``b``.
    if a is b:
        return True
    cdef Py_ssize_t sa
    cdef Py_ssize_t sb
    cdef const char *pa = uutf8_and_size(a, &sa)
    cdef const char *pb = uutf8_and_size(b, &sb)
    if sa != sb:
        return False
    if sa == 0:
        return True
    return memcmp(pa, pb, <size_t>sa) == 0


cdef inline void uintern_in_place(str s) except *:
    # Mutates the caller's PyObject* slot — Cython extension use only.
    cdef PyObject *p = <PyObject *>s
    PyUnicode_InternInPlace(&p)


cdef inline str unicode_from_string(const char *s):
    # Cheap sibling: str from C string (no intern). Mirror ``bytes_from_string``.
    return <str>PyUnicode_FromString(s)


cdef inline str uintern_from_string(const char *s):
    # Cheap sibling: intern from C string.
    return <str>PyUnicode_InternFromString(s)


cpdef inline bytes uutf8_bytes(str s):
    return PyUnicode_AsUTF8String(s)


cpdef inline str uintern(str s):
    cdef PyObject *p = <PyObject *>s
    PyUnicode_InternInPlace(&p)
    return <str>p


cpdef inline bint unicode_eq(str a, str b) noexcept:
    # Discoverability alias of ``str_eq`` (no divergent UCS path).
    return str_eq(a, b)


cdef inline bint ueq(str a, str b) noexcept:
    return str_eq(a, b)
