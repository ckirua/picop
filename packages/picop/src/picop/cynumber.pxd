# cynumber.pxd
# Number protocol helpers. Public docs in ``cynumber.pyi``.
# ``PyNumber_Divide`` / ``InPlaceDivide`` / ``Coerce``: ABI-missing on 3.14 — not wrapped.

from cpython.object cimport PyObject_RichCompare, Py_EQ


cdef extern from "Python.h":
    bint PyNumber_Check(object o) noexcept
    object PyNumber_Add(object o1, object o2)
    object PyNumber_Subtract(object o1, object o2)
    object PyNumber_Multiply(object o1, object o2)
    object PyNumber_MatrixMultiply(object o1, object o2)
    object PyNumber_FloorDivide(object o1, object o2)
    object PyNumber_TrueDivide(object o1, object o2)
    object PyNumber_Remainder(object o1, object o2)
    object PyNumber_Divmod(object o1, object o2)
    object PyNumber_Power(object o1, object o2, object o3)
    object PyNumber_Negative(object o)
    object PyNumber_Positive(object o)
    object PyNumber_Absolute(object o)
    object PyNumber_Invert(object o)
    object PyNumber_Lshift(object o1, object o2)
    object PyNumber_Rshift(object o1, object o2)
    object PyNumber_And(object o1, object o2)
    object PyNumber_Xor(object o1, object o2)
    object PyNumber_Or(object o1, object o2)
    object PyNumber_InPlaceAdd(object o1, object o2)
    object PyNumber_InPlaceSubtract(object o1, object o2)
    object PyNumber_InPlaceMultiply(object o1, object o2)
    object PyNumber_InPlaceMatrixMultiply(object o1, object o2)
    object PyNumber_InPlaceFloorDivide(object o1, object o2)
    object PyNumber_InPlaceTrueDivide(object o1, object o2)
    object PyNumber_InPlaceRemainder(object o1, object o2)
    object PyNumber_InPlacePower(object o1, object o2, object o3)
    object PyNumber_InPlaceLshift(object o1, object o2)
    object PyNumber_InPlaceRshift(object o1, object o2)
    object PyNumber_InPlaceAnd(object o1, object o2)
    object PyNumber_InPlaceXor(object o1, object o2)
    object PyNumber_InPlaceOr(object o1, object o2)
    object PyNumber_Long(object o)
    object PyNumber_Float(object o)
    object PyNumber_Index(object o)
    Py_ssize_t PyNumber_AsSsize_t(object o, object exc) except? -1
    bint PyIndex_Check(object o) noexcept


cpdef inline bint num_check(object o) noexcept:
    return PyNumber_Check(o)


cpdef inline bint num_index_check(object o) noexcept:
    return PyIndex_Check(o)


cdef inline bint neq_num(object a, object b):
    # Abstract number equality via RichCompare (Python ``==`` parity).
    # Do **not** use PyObject_RichCompareBool: it identity-shortcuts
    # ``nan is nan`` → True. Prefer ``long_eq`` / ``float_eq`` / ``complex_eq``
    # when the concrete type is known. Soft ``neq_num`` (not ``*_ne``).
    cdef object r = PyObject_RichCompare(a, b, Py_EQ)
    if r is True:
        return True
    if r is False:
        return False
    return bool(r)


cpdef inline bint num_eq(object a, object b):
    return neq_num(a, b)


cpdef inline object num_add(object o1, object o2):
    return PyNumber_Add(o1, o2)


cpdef inline object num_sub(object o1, object o2):
    return PyNumber_Subtract(o1, o2)


cpdef inline object num_mul(object o1, object o2):
    return PyNumber_Multiply(o1, o2)


cpdef inline object num_matmul(object o1, object o2):
    return PyNumber_MatrixMultiply(o1, o2)


cpdef inline object num_floordiv(object o1, object o2):
    return PyNumber_FloorDivide(o1, o2)


cpdef inline object num_truediv(object o1, object o2):
    return PyNumber_TrueDivide(o1, o2)


cpdef inline object num_mod(object o1, object o2):
    return PyNumber_Remainder(o1, o2)


cpdef inline object num_divmod(object o1, object o2):
    return PyNumber_Divmod(o1, o2)


cpdef inline object num_pow(object o1, object o2, object o3=None):
    return PyNumber_Power(o1, o2, o3)


cpdef inline object num_neg(object o):
    return PyNumber_Negative(o)


cpdef inline object num_pos(object o):
    return PyNumber_Positive(o)


cpdef inline object num_abs(object o):
    return PyNumber_Absolute(o)


cpdef inline object num_invert(object o):
    return PyNumber_Invert(o)


cpdef inline object num_lshift(object o1, object o2):
    return PyNumber_Lshift(o1, o2)


cpdef inline object num_rshift(object o1, object o2):
    return PyNumber_Rshift(o1, o2)


cpdef inline object num_and(object o1, object o2):
    return PyNumber_And(o1, o2)


cpdef inline object num_xor(object o1, object o2):
    return PyNumber_Xor(o1, o2)


cpdef inline object num_or(object o1, object o2):
    return PyNumber_Or(o1, o2)


cpdef inline object num_inplace_add(object o1, object o2):
    return PyNumber_InPlaceAdd(o1, o2)


cpdef inline object num_inplace_sub(object o1, object o2):
    return PyNumber_InPlaceSubtract(o1, o2)


cpdef inline object num_inplace_mul(object o1, object o2):
    return PyNumber_InPlaceMultiply(o1, o2)


cpdef inline object num_inplace_matmul(object o1, object o2):
    return PyNumber_InPlaceMatrixMultiply(o1, o2)


cpdef inline object num_inplace_floordiv(object o1, object o2):
    return PyNumber_InPlaceFloorDivide(o1, o2)


cpdef inline object num_inplace_truediv(object o1, object o2):
    return PyNumber_InPlaceTrueDivide(o1, o2)


cpdef inline object num_inplace_mod(object o1, object o2):
    return PyNumber_InPlaceRemainder(o1, o2)


cpdef inline object num_inplace_pow(object o1, object o2, object o3=None):
    return PyNumber_InPlacePower(o1, o2, o3)


cpdef inline object num_inplace_lshift(object o1, object o2):
    return PyNumber_InPlaceLshift(o1, o2)


cpdef inline object num_inplace_rshift(object o1, object o2):
    return PyNumber_InPlaceRshift(o1, o2)


cpdef inline object num_inplace_and(object o1, object o2):
    return PyNumber_InPlaceAnd(o1, o2)


cpdef inline object num_inplace_xor(object o1, object o2):
    return PyNumber_InPlaceXor(o1, o2)


cpdef inline object num_inplace_or(object o1, object o2):
    return PyNumber_InPlaceOr(o1, o2)


cpdef inline object num_long(object o):
    return PyNumber_Long(o)


cpdef inline object num_float(object o):
    return PyNumber_Float(o)


cpdef inline object num_index(object o):
    return PyNumber_Index(o)


cpdef inline Py_ssize_t num_as_ssize(object o, object exc=None) except? -1:
    return PyNumber_AsSsize_t(o, exc)
