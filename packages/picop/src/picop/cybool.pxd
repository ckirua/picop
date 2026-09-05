# cybool.pxd
# Boolean helpers. Public docs in ``cybool.pyi``.

from cpython.object cimport PyObject_RichCompareBool, Py_EQ


cdef extern from "Python.h":
    bint PyBool_Check(object o) noexcept
    object PyBool_FromLong(long v)


cpdef inline bint bool_check(object o) noexcept:
    return PyBool_Check(o)


cdef inline bint booleq(object a, object b):
    # Identity short-circuit + richcompare (same semantics as ``==``).
    # True/False are singletons — identity covers typed bool pairs.
    if a is b:
        return True
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cpdef inline bint bool_eq(object a, object b):
    return booleq(a, b)


cpdef inline object bool_from_long(long v):
    return PyBool_FromLong(v)


cpdef inline object bool_true():
    return PyBool_FromLong(1)


cpdef inline object bool_false():
    return PyBool_FromLong(0)
