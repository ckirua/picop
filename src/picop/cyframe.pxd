# cyframe.pxd
# CPython frame-object accessors.
# Public docs in ``cyframe.pyi``.
from cpython.object cimport PyObject
from cpython.pystate cimport PyFrameObject, PyThreadState


cdef extern from "Python.h":
    void Py_DECREF(PyObject *o)


cdef extern from "frameobject.h":
    ctypedef struct PyCodeObject:
        pass
    bint PyFrame_Check(object frame) noexcept
    int PyFrame_GetLineNumber(PyFrameObject *frame) noexcept
    int PyFrame_GetLasti(PyFrameObject *frame) noexcept
    object PyFrame_GetLocals(PyFrameObject *frame) noexcept
    object PyFrame_GetGlobals(PyFrameObject *frame) noexcept
    object PyFrame_GetBuiltins(PyFrameObject *frame) noexcept
    bint _PyFrame_IsEntryFrame(PyFrameObject *frame) noexcept

# Reference-returning getters route through the shim: they hand back a *new*
# reference, which Cython steals when declared as ``object``.  A ``PyObject *``
# declaration plus an ``<object>`` cast would incref it twice.
cdef extern from "cyframe_shim.h":
    object cy_frame_code(PyFrameObject *frame) noexcept
    object cy_frame_back(PyFrameObject *frame) noexcept
    object cy_frame_generator(PyFrameObject *frame) noexcept
    PyObject *cy_frame_var(PyFrameObject *frame, object name) except NULL
    PyObject *cy_frame_var_cstr(PyFrameObject *frame, const char *name) except NULL
    object cy_frame_new(PyThreadState *tstate, PyCodeObject *code, PyObject *globals, PyObject *locals)

cpdef inline bint frame_check(object frame) noexcept:
    return PyFrame_Check(frame)

cpdef inline int frame_lineno(object frame) noexcept:
    return PyFrame_GetLineNumber(<PyFrameObject *>frame)

cpdef inline int frame_lasti(object frame) noexcept:
    return PyFrame_GetLasti(<PyFrameObject *>frame)

cpdef inline object frame_code(object frame):
    return cy_frame_code(<PyFrameObject *>frame)

cpdef inline object frame_back(object frame):
    return cy_frame_back(<PyFrameObject *>frame)

cpdef inline object frame_locals(object frame):
    return PyFrame_GetLocals(<PyFrameObject *>frame)

cpdef inline object frame_globals(object frame):
    return PyFrame_GetGlobals(<PyFrameObject *>frame)

cpdef inline object frame_builtins(object frame):
    return PyFrame_GetBuiltins(<PyFrameObject *>frame)

cpdef inline object frame_generator(object frame):
    return cy_frame_generator(<PyFrameObject *>frame)

cpdef inline object frame_var(object frame, object name):
    # ``cy_frame_var`` hands back a new reference; convert first, then release
    # the raw pointer so exactly one reference reaches the caller.
    cdef PyObject *value = cy_frame_var(<PyFrameObject *>frame, name)
    cdef object result = <object>value
    Py_DECREF(value)
    return result

cpdef inline object frame_var_cstr(object frame, const char *name):
    cdef PyObject *value = cy_frame_var_cstr(<PyFrameObject *>frame, name)
    cdef object result = <object>value
    Py_DECREF(value)
    return result

cdef inline object frame_new(PyThreadState *tstate, PyCodeObject *code, PyObject *globals, PyObject *locals):
    return cy_frame_new(tstate, code, globals, locals)

cdef inline bint frame_is_entry_frame(PyFrameObject *frame) noexcept:
    return _PyFrame_IsEntryFrame(frame)
