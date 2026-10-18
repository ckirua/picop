# cyfloat.pxd
# ``float`` helpers. Public docs in ``cyfloat.pyi``.
# ``AS_DOUBLE`` unchecked: also exposed as cdef alias.

from cpython.object cimport PyObject_RichCompare, Py_EQ

cdef extern from "Python.h":
    bint PyFloat_Check(object p) noexcept
    bint PyFloat_CheckExact(object p) noexcept
    object PyFloat_FromString(object str)
    object PyFloat_FromDouble(double v)
    double PyFloat_AsDouble(object pyfloat) except? -1
    double PyFloat_AS_DOUBLE(object pyfloat) noexcept


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
