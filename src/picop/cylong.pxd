# cylong.pxd
# ``int`` / long helpers. Public docs in ``cylong.pyi``.
# Pointer/overflow out-params and FromString: cdef (+ tuple wrappers where useful).

from libc.stddef cimport size_t
from cpython.object cimport PyObject_RichCompareBool, Py_EQ


cdef extern from "Python.h":
    ctypedef long long PY_LONG_LONG
    ctypedef unsigned long long uPY_LONG_LONG "unsigned long long"

    bint PyLong_Check(object p) noexcept
    bint PyLong_CheckExact(object p) noexcept
    object PyLong_FromLong(long v)
    object PyLong_FromUnsignedLong(unsigned long v)
    object PyLong_FromSsize_t(Py_ssize_t v)
    object PyLong_FromSize_t(size_t v)
    object PyLong_FromLongLong(PY_LONG_LONG v)
    object PyLong_FromUnsignedLongLong(uPY_LONG_LONG v)
    object PyLong_FromDouble(double v)
    object PyLong_FromString(const char *str, char **pend, int base)
    object PyLong_FromVoidPtr(void *p)
    long PyLong_AsLong(object pylong) except? -1
    long PyLong_AsLongAndOverflow(object pylong, int *overflow) except? -1
    PY_LONG_LONG PyLong_AsLongLongAndOverflow(object pylong, int *overflow) except? -1
    Py_ssize_t PyLong_AsSsize_t(object pylong) except? -1
    unsigned long PyLong_AsUnsignedLong(object pylong) except? -1
    PY_LONG_LONG PyLong_AsLongLong(object pylong) except? -1
    uPY_LONG_LONG PyLong_AsUnsignedLongLong(object pylong) except? -1
    unsigned long PyLong_AsUnsignedLongMask(object io) noexcept
    uPY_LONG_LONG PyLong_AsUnsignedLongLongMask(object io) noexcept
    double PyLong_AsDouble(object pylong) except? -1.0
    void *PyLong_AsVoidPtr(object pylong) except? NULL


cpdef inline bint long_check(object p) noexcept:
    return PyLong_Check(p)


cpdef inline bint long_check_exact(object p) noexcept:
    return PyLong_CheckExact(p)


cdef inline bint loeq(object a, object b):
    # Identity short-circuit + richcompare (same semantics as ``==``).
    if a is b:
        return True
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cpdef inline object long_from_long(long v):
    return PyLong_FromLong(v)


cpdef inline object long_from_ulong(unsigned long v):
    return PyLong_FromUnsignedLong(v)


cpdef inline object long_from_ssize(Py_ssize_t v):
    return PyLong_FromSsize_t(v)


cpdef inline object long_from_size(size_t v):
    return PyLong_FromSize_t(v)


cpdef inline object long_from_longlong(PY_LONG_LONG v):
    return PyLong_FromLongLong(v)


cpdef inline object long_from_ulonglong(uPY_LONG_LONG v):
    return PyLong_FromUnsignedLongLong(v)


cpdef inline object long_from_double(double v):
    return PyLong_FromDouble(v)


cpdef inline long long_as_long(object pylong) except? -1:
    return PyLong_AsLong(pylong)


cpdef inline tuple long_as_long_overflow(object pylong):
    cdef int overflow = 0
    cdef long v = PyLong_AsLongAndOverflow(pylong, &overflow)
    return (v, overflow)


cpdef inline Py_ssize_t long_as_ssize(object pylong) except? -1:
    return PyLong_AsSsize_t(pylong)


cpdef inline unsigned long long_as_ulong(object pylong) except? -1:
    return PyLong_AsUnsignedLong(pylong)


cpdef inline PY_LONG_LONG long_as_longlong(object pylong) except? -1:
    return PyLong_AsLongLong(pylong)


cpdef inline uPY_LONG_LONG long_as_ulonglong(object pylong) except? -1:
    return PyLong_AsUnsignedLongLong(pylong)


cpdef inline unsigned long long_as_ulong_mask(object io) noexcept:
    return PyLong_AsUnsignedLongMask(io)


cpdef inline uPY_LONG_LONG long_as_ulonglong_mask(object io) noexcept:
    return PyLong_AsUnsignedLongLongMask(io)


cpdef inline double long_as_double(object pylong) except? -1.0:
    return PyLong_AsDouble(pylong)


cdef inline object long_from_string(const char *s, int base=10):
    return PyLong_FromString(s, NULL, base)


cdef inline object long_from_voidptr(void *p):
    return PyLong_FromVoidPtr(p)


cdef inline void *long_as_voidptr(object pylong) except? NULL:
    return PyLong_AsVoidPtr(pylong)


cdef inline PY_LONG_LONG long_as_longlong_overflow(object pylong, int *overflow) except? -1:
    return PyLong_AsLongLongAndOverflow(pylong, overflow)


cpdef inline bint long_eq(object a, object b):
    return loeq(a, b)


cpdef inline bint int_eq(object a, object b):
    # Discoverability alias of ``long_eq`` (same semantics).
    return loeq(a, b)
