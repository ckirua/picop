# cymethod.pxd
# Bound-method and C-function helpers. Public docs in ``cymethod.pyi``.
# Prefer ``method_get_*`` (checked). Unchecked GET_* macros: ``*_unchecked``.
# ``PyMethod_Class`` ABI-missing on 3.14. ``PyCFunction_GetFunction`` hands out a
# raw C pointer, never a Python object — it is never exposed as an object.

from cpython.object cimport PyObject, PyObject_RichCompareBool, Py_EQ
import cython


cdef extern from "Python.h":
    bint PyMethod_Check(object o) noexcept
    object PyMethod_New(object func, object self)
    PyObject *PyMethod_Function(object meth) except? NULL
    PyObject *PyMethod_Self(object meth) except? NULL
    PyObject *PyMethod_GET_FUNCTION(object meth) noexcept
    PyObject *PyMethod_GET_SELF(object meth) noexcept
    bint PyCFunction_Check(object o) noexcept
    bint PyCFunction_CheckExact(object o) noexcept
    bint PyCMethod_CheckExact(object o) noexcept
    bint PyCMethod_Check(object o) noexcept
    PyObject *PyCFunction_GetSelf(object func) except? NULL
    void *PyCFunction_GET_FUNCTION(object func) noexcept
    PyObject *PyCFunction_GET_SELF(object func) noexcept
    int PyCFunction_GET_FLAGS(object func) noexcept
    PyObject *PyCFunction_GET_CLASS(object func) noexcept
    object PyClassMethod_New(object callable)
    object PyStaticMethod_New(object callable)


cdef inline object _borrowed_to_owned(PyObject *p):
    if p is NULL:
        return None
    return <object>p


cpdef inline bint method_check(object o) noexcept:
    return PyMethod_Check(o)


cpdef inline bint cfunction_check(object o) noexcept:
    return PyCFunction_Check(o)


cpdef inline bint cfunction_check_exact(object o) noexcept:
    return PyCFunction_CheckExact(o)


cpdef inline bint cmethod_check(object o) noexcept:
    return PyCMethod_Check(o)


cpdef inline bint cmethod_check_exact(object o) noexcept:
    return PyCMethod_CheckExact(o)


cpdef inline object method_new(object func, object self):
    return PyMethod_New(func, self)


cpdef inline object classmethod_new(object callable):
    return PyClassMethod_New(callable)


cpdef inline object staticmethod_new(object callable):
    return PyStaticMethod_New(callable)


cpdef inline object cfunction_get_self(object func):
    cdef PyObject *p
    cdef object result
    with cython.critical_section(func):
        p = PyCFunction_GetSelf(func)
        result = _borrowed_to_owned(p)
    return result


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


cdef inline object method_function(object meth):
    cdef object result
    with cython.critical_section(meth):
        result = _borrowed_to_owned(PyMethod_Function(meth))
    return result


cdef inline object method_self(object meth):
    cdef object result
    with cython.critical_section(meth):
        result = _borrowed_to_owned(PyMethod_Self(meth))
    return result


cdef inline object method_function_unchecked(object meth):
    # Unchecked macro — meth must be a method.
    cdef object result
    with cython.critical_section(meth):
        result = _borrowed_to_owned(PyMethod_GET_FUNCTION(meth))
    return result


cdef inline object method_self_unchecked(object meth):
    # Unchecked macro — meth must be a method.
    cdef object result
    with cython.critical_section(meth):
        result = _borrowed_to_owned(PyMethod_GET_SELF(meth))
    return result


cdef inline object cfunction_get_self_unchecked(object func):
    # Unchecked macro — func must be a C function; NULL for METH_STATIC.
    cdef object result
    with cython.critical_section(func):
        result = _borrowed_to_owned(PyCFunction_GET_SELF(func))
    return result


cdef inline int cfunction_get_flags_unchecked(object func) noexcept:
    # Unchecked macro — METH_VARARGS / METH_KEYWORDS / METH_STATIC / METH_METHOD bits.
    with cython.critical_section(func):
        return PyCFunction_GET_FLAGS(func)


cdef inline object cfunction_get_class_unchecked(object func):
    # Unchecked macro — the defining class for METH_METHOD, else None.
    cdef object result
    with cython.critical_section(func):
        result = _borrowed_to_owned(<PyObject *>PyCFunction_GET_CLASS(func))
    return result


cdef inline void *cfunction_get_function_unchecked(object func) noexcept:
    # Raw C entry point, not a Python object — never incref it.
    with cython.critical_section(func):
        return PyCFunction_GET_FUNCTION(func)


# N6: preferred method_get_* (0.3: method_function/method_self cdef-only)
cpdef inline object method_get_function(object meth):
    return method_function(meth)

cpdef inline object method_get_self(object meth):
    return method_self(meth)
