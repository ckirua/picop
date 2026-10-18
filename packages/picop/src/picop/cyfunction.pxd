# cyfunction.pxd
# Function-object helpers. Public docs in ``cyfunction.pyi``.
# Borrowed getters are promoted to owning Cython locals under the function lock.

from cpython.object cimport PyObject
import cython


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
    # Conversion from PyObject* to Cython object retains the borrowed value.
    return <object>p

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
    cdef PyObject *p
    cdef object result
    with cython.critical_section(op):
        p = PyFunction_GetCode(op)
        result = _borrowed_to_owned(p)
    return result


cpdef inline object func_get_globals(object op):
    cdef PyObject *p
    cdef object result
    with cython.critical_section(op):
        p = PyFunction_GetGlobals(op)
        result = _borrowed_to_owned(p)
    return result


cpdef inline object func_get_module(object op):
    cdef PyObject *p
    cdef object result
    with cython.critical_section(op):
        p = PyFunction_GetModule(op)
        result = _borrowed_to_owned(p)
    return result


cpdef inline object func_get_defaults(object op):
    cdef PyObject *p
    cdef object result
    with cython.critical_section(op):
        p = PyFunction_GetDefaults(op)
        result = _borrowed_to_owned(p)
    return result

cpdef inline int func_set_defaults(object op, object defaults) except -1:
    with cython.critical_section(op):
        return PyFunction_SetDefaults(op, defaults)


cpdef inline object func_get_closure(object op):
    cdef PyObject *p
    cdef object result
    with cython.critical_section(op):
        p = PyFunction_GetClosure(op)
        result = _borrowed_to_owned(p)
    return result


cpdef inline int func_set_closure(object op, object closure) except -1:
    with cython.critical_section(op):
        return PyFunction_SetClosure(op, closure)
