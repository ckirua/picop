# cycontextvars.pxd
# contextvars helpers. Public docs in ``cycontextvars.pyi``.

from cpython.object cimport PyObject, PyObject_RichCompareBool, Py_EQ


cdef extern from "Python.h":
    bint PyContext_CheckExact(object obj) noexcept
    bint PyContextVar_CheckExact(object obj) noexcept
    bint PyContextToken_CheckExact(object obj) noexcept
    object PyContext_New()
    object PyContext_Copy(object ctx)
    object PyContext_CopyCurrent()
    int PyContext_Enter(object ctx) except -1
    int PyContext_Exit(object ctx) except -1
    object PyContextVar_New(const char *name, object default_value)
    object PyContextVar_Set(object var, object value)
    int PyContextVar_Reset(object var, object token) except -1


cpdef inline bint ctx_check_exact(object obj) noexcept:
    return PyContext_CheckExact(obj)


cpdef inline bint ctxvar_check_exact(object obj) noexcept:
    return PyContextVar_CheckExact(obj)


cpdef inline bint ctxtoken_check_exact(object obj) noexcept:
    return PyContextToken_CheckExact(obj)


cdef inline bint ctxeq(object a, object b):
    # ``Context`` value equality (mapping of vars→values), not identity.
    # ``ContextVar`` / ``Token`` stay identity — use ``obj_eq``; no dedicated helpers.
    if a is b:
        return True
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cpdef inline bint context_eq(object a, object b):
    return ctxeq(a, b)


cpdef inline object ctx_new():
    return PyContext_New()


cpdef inline object ctx_copy(object ctx):
    return PyContext_Copy(ctx)


cpdef inline object ctx_copy_current():
    return PyContext_CopyCurrent()


cpdef inline int ctx_enter(object ctx) except -1:
    return PyContext_Enter(ctx)


cpdef inline int ctx_exit(object ctx) except -1:
    return PyContext_Exit(ctx)


cpdef inline object ctxvar_new(const char *name, object default_value=None):
    return PyContextVar_New(name, default_value)


cpdef inline object ctxvar_set(object var, object value):
    return PyContextVar_Set(var, value)


cpdef inline int ctxvar_reset(object var, object token) except -1:
    return PyContextVar_Reset(var, token)
