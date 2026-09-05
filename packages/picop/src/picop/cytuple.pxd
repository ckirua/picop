# cytuple.pxd
# Typed ``tuple`` helpers. Public docs live in ``cytuple.pyi``.
# ``tnew`` / ``tset`` / ``tresize`` are cdef (cimport only) — see docs/modules/001_cytuple.md.

from cpython.object cimport PyObject, PyObject_RichCompareBool, Py_EQ
from cpython.ref cimport Py_INCREF
from cpython.tuple cimport (
    PyTuple_Check,
    PyTuple_CheckExact,
    PyTuple_GetItem,
    PyTuple_GetSlice,
    PyTuple_New,
    PyTuple_Size,
)

cdef extern from "Python.h":
    PyObject* PyTuple_GET_ITEM(object p, Py_ssize_t pos) noexcept
    Py_ssize_t PyTuple_GET_SIZE(object p) noexcept
    void PyTuple_SET_ITEM(object p, Py_ssize_t pos, object o) noexcept
    int PyTuple_SetItem(object p, Py_ssize_t pos, object o) except -1
    tuple PyTuple_Pack(Py_ssize_t n, ...)
    int _PyTuple_Resize(PyObject **p, Py_ssize_t newsize) except -1


cdef inline bint tcheck(object p) noexcept:
    return PyTuple_Check(p)


cdef inline bint tcheck_exact(object p) noexcept:
    return PyTuple_CheckExact(p)


cdef inline tuple tnew(Py_ssize_t n):
    # Uninitialized slots; fill with tset before exposing to Python.
    return PyTuple_New(n)


cdef inline tuple tpack2(object a, object b):
    return PyTuple_Pack(2, <PyObject*>a, <PyObject*>b)


cdef inline tuple tpack3(object a, object b, object c):
    return PyTuple_Pack(3, <PyObject*>a, <PyObject*>b, <PyObject*>c)


cdef inline tuple tpack4(object a, object b, object c, object d):
    return PyTuple_Pack(4, <PyObject*>a, <PyObject*>b, <PyObject*>c, <PyObject*>d)


cdef inline Py_ssize_t tsize(tuple t) except -1:
    return PyTuple_Size(t)


cdef inline object tget(tuple t, Py_ssize_t i) noexcept:
    # No bounds check.
    return <object>PyTuple_GET_ITEM(t, i)


cdef inline object tget_checked(tuple t, Py_ssize_t i):
    return <object>PyTuple_GetItem(t, i)


cdef inline Py_ssize_t tlen(tuple t) noexcept:
    return PyTuple_GET_SIZE(t)


cdef inline bint teq(tuple a, tuple b):
    if a is b:
        return True
    if PyTuple_GET_SIZE(a) != PyTuple_GET_SIZE(b):
        return False
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cdef inline tuple tslice(tuple t, Py_ssize_t low, Py_ssize_t high):
    return PyTuple_GetSlice(t, low, high)


cdef inline int tset(tuple t, Py_ssize_t i, object value) except -1:
    # SET_ITEM + INCREF; unique-ref SetItem fails after Python bind.
    Py_INCREF(value)
    PyTuple_SET_ITEM(t, i, value)
    return 0


cdef inline tuple tresize(tuple t, Py_ssize_t newsize):
    # Requires unique refcnt==1; else SystemError.
    cdef PyObject *p = <PyObject*>t
    cdef int rc = _PyTuple_Resize(&p, newsize)
    if rc < 0 or p is NULL:
        return None
    return <tuple>p

# Wave 4 N1/N5 preferred names (0.3: soft letter/bare are cdef-only)

cpdef inline bint tuple_check(object p) noexcept:
    return tcheck(p)

cpdef inline bint tuple_check_exact(object p) noexcept:
    return tcheck_exact(p)

cpdef inline object tuple_get(tuple t, Py_ssize_t i) noexcept:
    return tget(t, i)

cpdef inline object tuple_get_checked(tuple t, Py_ssize_t i):
    return tget_checked(t, i)

cpdef inline Py_ssize_t tuple_len(tuple t) noexcept:
    return tlen(t)

cpdef inline bint tuple_eq(tuple a, tuple b):
    return teq(a, b)

cdef inline tuple tuple_new(Py_ssize_t n):
    return tnew(n)

cpdef inline tuple tuple_pack2(object a, object b):
    return tpack2(a, b)

cpdef inline tuple tuple_pack3(object a, object b, object c):
    return tpack3(a, b, c)

cpdef inline tuple tuple_pack4(object a, object b, object c, object d):
    return tpack4(a, b, c, d)

cdef inline tuple tuple_resize(tuple t, Py_ssize_t newsize):
    return tresize(t, newsize)

cdef inline int tuple_set(tuple t, Py_ssize_t i, object value) except -1:
    return tset(t, i, value)

cpdef inline Py_ssize_t tuple_size(tuple t) except -1:
    return tsize(t)

cpdef inline tuple tuple_slice(tuple t, Py_ssize_t low, Py_ssize_t high):
    return tslice(t, low, high)

