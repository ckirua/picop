# cymethod.pxd
# Bound-method helpers. Public docs in ``cymethod.pyi``.
# Prefer ``method_get_*`` (checked). Unchecked GET_* macros: ``method_*_unchecked``.
# ``PyMethod_Class`` ABI-missing on 3.14.

from cpython.object cimport PyObject, PyObject_RichCompareBool, Py_EQ
from cpython.ref cimport Py_INCREF


cdef extern from "Python.h":
    bint PyMethod_Check(object o) noexcept
    object PyMethod_New(object func, object self)
    PyObject *PyMethod_Function(object meth) except? NULL
    PyObject *PyMethod_Self(object meth) except? NULL
    PyObject *PyMethod_GET_FUNCTION(object meth) noexcept
    PyObject *PyMethod_GET_SELF(object meth) noexcept


cdef inline object _borrowed_to_owned(PyObject *p):
    if p is NULL:
        return None
    cdef object obj = <object>p
    Py_INCREF(obj)
    return obj


cpdef inline bint method_check(object o) noexcept:
    return PyMethod_Check(o)


cdef inline bint methodeq(object a, object b) except -1:
    # Bound-method equality matches CPython ``method_richcompare``: same
    # function + same ``__self__`` (not identity — ``c.m == c.m`` can be
    # True for distinct method objects). Soft ``methodeq``. Callers should
    # pass method objects. Not on ``hot``.
    if a is b:
        return True
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cpdef inline bint method_eq(object a, object b) except -1:
    return methodeq(a, b)


cpdef inline object method_new(object func, object self):
    return PyMethod_New(func, self)


cdef inline object method_function(object meth):
    return _borrowed_to_owned(PyMethod_Function(meth))


cdef inline object method_self(object meth):
    return _borrowed_to_owned(PyMethod_Self(meth))


cdef inline object method_function_unchecked(object meth):
    # Unchecked macro — meth must be a method.
    return _borrowed_to_owned(PyMethod_GET_FUNCTION(meth))


cdef inline object method_self_unchecked(object meth):
    # Unchecked macro — meth must be a method.
    return _borrowed_to_owned(PyMethod_GET_SELF(meth))

# N6: preferred method_get_* (0.3: method_function/method_self cdef-only)
cpdef inline object method_get_function(object meth):
    return method_function(meth)

cpdef inline object method_get_self(object meth):
    return method_self(meth)
