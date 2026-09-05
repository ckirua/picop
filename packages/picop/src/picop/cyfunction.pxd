# cyfunction.pxd
# Function-object helpers. Public docs in ``cyfunction.pyi``.
# Getters return owned refs (INCREF of borrowed C-API results).

from cpython.object cimport PyObject
from cpython.ref cimport Py_INCREF


cdef extern from "Python.h":
    bint PyFunction_Check(object o) noexcept
    object PyFunction_New(object code, object globals)
    PyObject *PyFunction_GetCode(object op) except? NULL
    PyObject *PyFunction_GetGlobals(object op) except? NULL
    PyObject *PyFunction_GetModule(object op) except? NULL
    PyObject *PyFunction_GetDefaults(object op) except? NULL
    int PyFunction_SetDefaults(object op, object defaults) except -1
    PyObject *PyFunction_GetClosure(object op) except? NULL
    int PyFunction_SetClosure(object op, object closure) except -1


cdef inline object _borrowed_to_owned(PyObject *p):
    if p is NULL:
        return None
    cdef object obj = <object>p
    Py_INCREF(obj)
    return obj


cpdef inline bint func_check(object o) noexcept:
    return PyFunction_Check(o)


cdef inline bint funceq(object a, object b) noexcept:
    # Function equality is identity (CPython uses ``object.__eq__``). Soft
    # ``funceq``. Callers should pass function objects. Not on ``hot``.
    return a is b


cpdef inline bint func_eq(object a, object b) noexcept:
    return funceq(a, b)


cpdef inline object func_new(object code, object globals):
    return PyFunction_New(code, globals)


cpdef inline object func_get_code(object op):
    return _borrowed_to_owned(PyFunction_GetCode(op))


cpdef inline object func_get_globals(object op):
    return _borrowed_to_owned(PyFunction_GetGlobals(op))


cpdef inline object func_get_module(object op):
    return _borrowed_to_owned(PyFunction_GetModule(op))


cpdef inline object func_get_defaults(object op):
    return _borrowed_to_owned(PyFunction_GetDefaults(op))


cpdef inline int func_set_defaults(object op, object defaults) except -1:
    return PyFunction_SetDefaults(op, defaults)


cpdef inline object func_get_closure(object op):
    return _borrowed_to_owned(PyFunction_GetClosure(op))


cpdef inline int func_set_closure(object op, object closure) except -1:
    return PyFunction_SetClosure(op, closure)
