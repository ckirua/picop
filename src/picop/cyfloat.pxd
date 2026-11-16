# cyfloat.pxd
# ``float`` helpers. Public docs in ``cyfloat.pyi``.
# ``AS_DOUBLE`` unchecked: also exposed as cdef alias.

from cpython.object cimport PyObject_RichCompare, Py_EQ

from cpython.bytes cimport PyBytes_FromStringAndSize
cdef extern from "Python.h":
    bint PyFloat_Check(object p) noexcept
    bint PyFloat_CheckExact(object p) noexcept
    object PyFloat_FromString(object str)
    object PyFloat_FromDouble(double v)
    double PyFloat_AsDouble(object pyfloat) except? -1
    double PyFloat_AS_DOUBLE(object pyfloat) noexcept
    int PyFloat_Pack8(double x, char *p, int le) except -1
    int PyFloat_Pack4(double x, char *p, int le) except -1
    int PyFloat_Pack2(double x, char *p, int le) except -1
    double PyFloat_Unpack8(const char *p, int le) except? -1
    double PyFloat_Unpack4(const char *p, int le) except? -1
    double PyFloat_Unpack2(const char *p, int le) except? -1
    bint PyBytes_Check(object)
    Py_ssize_t PyBytes_GET_SIZE(object)
    char *PyBytes_AS_STRING(object)

cpdef inline object float_pack8(double value, bint little_endian=True):
    cdef char buf[8]
    PyFloat_Pack8(value, buf, <int>little_endian)
    return PyBytes_FromStringAndSize(buf, 8)

cpdef inline object float_pack4(double value, bint little_endian=True):
    cdef char buf[4]
    PyFloat_Pack4(value, buf, <int>little_endian)
    return PyBytes_FromStringAndSize(buf, 4)

cpdef inline object float_pack2(double value, bint little_endian=True):
    cdef char buf[2]
    PyFloat_Pack2(value, buf, <int>little_endian)
    return PyBytes_FromStringAndSize(buf, 2)
cpdef inline double float_unpack8(object data, bint little_endian=True) except? 0.0:
    if not PyBytes_Check(data):
        raise TypeError("expected a bytes object")
    if PyBytes_GET_SIZE(data) < 8:
        raise ValueError("unpack requires at least 8 bytes")
    return PyFloat_Unpack8(PyBytes_AS_STRING(data), <int>little_endian)

cpdef inline double float_unpack4(object data, bint little_endian=True) except? 0.0:
    if not PyBytes_Check(data):
        raise TypeError("expected a bytes object")
    if PyBytes_GET_SIZE(data) < 4:
        raise ValueError("unpack requires at least 4 bytes")
    return PyFloat_Unpack4(PyBytes_AS_STRING(data), <int>little_endian)

cpdef inline double float_unpack2(object data, bint little_endian=True) except? 0.0:
    if not PyBytes_Check(data):
        raise TypeError("expected a bytes object")
    if PyBytes_GET_SIZE(data) < 2:
        raise ValueError("unpack requires at least 2 bytes")
    return PyFloat_Unpack2(PyBytes_AS_STRING(data), <int>little_endian)

cpdef inline bint float_check(object p) noexcept:
    return PyFloat_Check(p)


cpdef inline bint float_check_exact(object p) noexcept:
    return PyFloat_CheckExact(p)


cdef inline bint feq(object a, object b):
    # Float/float: C ``double ==`` (IEEE NaN != NaN, +0.0 == -0.0 — Python parity).
    # Do **not** use PyObject_RichCompareBool: it identity-shortcuts ``nan is nan`` → True.
    if PyFloat_Check(a) and PyFloat_Check(b):
        return PyFloat_AS_DOUBLE(a) == PyFloat_AS_DOUBLE(b)
    cdef object r = PyObject_RichCompare(a, b, Py_EQ)
    if r is True:
        return True
    if r is False:
        return False
    return bool(r)


cpdef inline bint float_eq(object a, object b):
    return feq(a, b)


cpdef inline object float_from_double(double v):
    return PyFloat_FromDouble(v)


cdef inline object float_from_string(object s):
    return PyFloat_FromString(s)


cpdef inline double float_as_double(object pyfloat) except? -1:
    return PyFloat_AsDouble(pyfloat)


cdef inline double float_as_double_unchecked(object pyfloat) noexcept:
    # No type check — UB if not a float.
    return PyFloat_AS_DOUBLE(pyfloat)
# N2 preferred *_cstr (0.3: *_string cdef-only where soft)

cpdef inline object float_from_cstr(object s):
    return float_from_string(s)
