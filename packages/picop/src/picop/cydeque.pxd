# cydeque.pxd
# ``collections.deque`` helpers. Public docs in ``cydeque.pyi``.

from cpython.object cimport PyObject_RichCompareBool, Py_EQ


cdef inline bint dqeq(object a, object b):
    # Identity short-circuit + richcompare (same semantics as ``deque.__eq__``).
    if a is b:
        return True
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cpdef inline bint deque_eq(object a, object b):
    return dqeq(a, b)
