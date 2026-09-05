# cyrange.pxd
# ``range`` helpers. Public docs in ``cyrange.pyi``.

from cpython.object cimport PyObject_RichCompareBool, Py_EQ


cdef inline bint rqeq(object a, object b):
    # Identity short-circuit + richcompare (same semantics as ``range.__eq__``).
    if a is b:
        return True
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cpdef inline bint range_eq(object a, object b):
    return rqeq(a, b)
