# cyfunction.pxd
# Function-object helpers. Public docs in ``cyfunction.pyi``.
# Borrowed getters are promoted to owning Cython locals under the function lock.

from cpython.object cimport PyObject
from cpython.unicode cimport PyUnicode_Check
import cython


cdef extern from "Python.h":
    bint PyFunction_Check(object o) noexcept
    bint PyCode_Check(object o) noexcept
    object PyFunction_New(object code, object globals)
    object PyFunction_NewWithQualName(object code, object globals, object qualname)
    PyObject *PyFunction_GetCode(object op) except? NULL
    PyObject *PyFunction_GetGlobals(object op) except? NULL
    PyObject *PyFunction_GetModule(object op) except? NULL
    PyObject *PyFunction_GetDefaults(object op) except? NULL
    int PyFunction_SetDefaults(object op, object defaults) except -1
    PyObject *PyFunction_GetClosure(object op) except? NULL
    int PyFunction_SetClosure(object op, object closure) except -1
    PyObject *PyFunction_GetKwDefaults(object op) except? NULL
    int PyFunction_SetKwDefaults(object op, object defaults) except -1
    PyObject *PyFunction_GetAnnotations(object op) except? NULL
    int PyFunction_SetAnnotations(object op, object annotations) except -1
    # Unchecked macros: borrowed field refs, no type check, trusted caller.
    PyObject *PyFunction_GET_CODE(object op) noexcept
    PyObject *PyFunction_GET_GLOBALS(object op) noexcept
    PyObject *PyFunction_GET_MODULE(object op) noexcept
    PyObject *PyFunction_GET_DEFAULTS(object op) noexcept
    PyObject *PyFunction_GET_KW_DEFAULTS(object op) noexcept
    PyObject *PyFunction_GET_CLOSURE(object op) noexcept
    PyObject *PyFunction_GET_ANNOTATIONS(object op) noexcept

    # Function watchers (CPython 3.12+): per-interpreter lifecycle callbacks.
    # The callback is a C function pointer, so this surface is cimport-only.
    # CPython hands the callback a *borrowed* reference to the function and, for
    # MODIFY_* events, a borrowed reference to the value about to be stored; the
    # callback may inspect but must not modify `func`. Exceptions returned with
    # -1 are reported as unraisable; preserve any pending exception on entry.
    # PyFunction_EVENT_MODIFY_QUALNAME is CPython 3.15+; guard its use.
    ctypedef enum PyFunction_WatchEvent:
        PyFunction_EVENT_CREATE
        PyFunction_EVENT_DESTROY
        PyFunction_EVENT_MODIFY_CODE
        PyFunction_EVENT_MODIFY_DEFAULTS
        PyFunction_EVENT_MODIFY_KWDEFAULTS
        PyFunction_EVENT_MODIFY_QUALNAME
    ctypedef struct PyFunctionObject:
        pass
    ctypedef int (*PyFunction_WatchCallback)(
        PyFunction_WatchEvent event,
        PyFunctionObject *func,
        PyObject *new_value,
    ) except -1
    int PyFunction_AddWatcher(PyFunction_WatchCallback callback) except? -1
    int PyFunction_ClearWatcher(int watcher_id) except? -1


cdef extern from "cyfunction_shim.h":
    int picop_func_event_modify_qualname() noexcept


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
    if not PyCode_Check(code) or globals is None:
        raise TypeError("func_new() requires a code object and a globals dict")
    return PyFunction_New(code, globals)


cpdef inline object func_new_with_qualname(object code, object globals, object qualname):
    if not PyCode_Check(code) or globals is None:
        raise TypeError("func_new_with_qualname() requires a code object and a globals dict")
    if qualname is None:
        qualname = ""
    elif not PyUnicode_Check(qualname):
        raise TypeError("func_new_with_qualname() qualname must be a str or None")
    return PyFunction_NewWithQualName(code, globals, qualname)


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


cpdef inline object func_get_kw_defaults(object op):
    cdef PyObject *p
    cdef object result
    with cython.critical_section(op):
        p = PyFunction_GetKwDefaults(op)
        result = _borrowed_to_owned(p)
    return result


cpdef inline int func_set_kw_defaults(object op, object defaults) except -1:
    with cython.critical_section(op):
        return PyFunction_SetKwDefaults(op, defaults)


cpdef inline object func_get_annotations(object op):
    cdef PyObject *p
    cdef object result
    with cython.critical_section(op):
        p = PyFunction_GetAnnotations(op)
        result = _borrowed_to_owned(p)
    return result


cpdef inline int func_set_annotations(object op, object annotations) except -1:
    with cython.critical_section(op):
        return PyFunction_SetAnnotations(op, annotations)


# Unchecked macro getters (cimport-only): no type check, borrowed field refs
# promoted to owning refs. Caller must have a function object.
cdef inline object func_get_code_unchecked(object op):
    return _borrowed_to_owned(PyFunction_GET_CODE(op))


cdef inline object func_get_globals_unchecked(object op):
    return _borrowed_to_owned(PyFunction_GET_GLOBALS(op))


cdef inline object func_get_module_unchecked(object op):
    return _borrowed_to_owned(PyFunction_GET_MODULE(op))


cdef inline object func_get_defaults_unchecked(object op):
    return _borrowed_to_owned(PyFunction_GET_DEFAULTS(op))


cdef inline object func_get_kw_defaults_unchecked(object op):
    return _borrowed_to_owned(PyFunction_GET_KW_DEFAULTS(op))


cdef inline object func_get_annotations_unchecked(object op):
    return _borrowed_to_owned(PyFunction_GET_ANNOTATIONS(op))


cdef inline object func_get_closure_unchecked(object op):
    return _borrowed_to_owned(PyFunction_GET_CLOSURE(op))


# Function watchers (cimport-only). Registration is per-interpreter and global:
# the callback sees every function created, destroyed, or modified while it is
# registered. `func_add_watcher` returns the handle accepted by
# `func_clear_watcher`; both raise on -1 (no handles left / unknown id).
cdef inline int func_add_watcher(PyFunction_WatchCallback callback) except? -1:
    return PyFunction_AddWatcher(callback)


cdef inline int func_clear_watcher(int watcher_id) except? -1:
    return PyFunction_ClearWatcher(watcher_id)


cdef inline int func_event_modify_qualname() noexcept:
    # -1 on CPython 3.14, the event id on 3.15+; lets callers branch at runtime
    # instead of carrying a Cython compile-time conditional.
    return picop_func_event_modify_qualname()
