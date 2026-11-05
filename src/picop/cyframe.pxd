# cyframe.pxd
# CPython frame-object accessors.
# Public docs in ``cyframe.pyi``.
from cpython.object cimport PyObject
from cpython.pystate cimport PyFrameObject, PyThreadState


cdef extern from "frameobject.h":
    ctypedef struct PyCodeObject:
        pass
    bint PyFrame_Check(object frame) noexcept
    int PyFrame_GetLineNumber(PyFrameObject *frame) noexcept
    int PyFrame_GetLasti(PyFrameObject *frame) noexcept
    PyCodeObject *PyFrame_GetCode(PyFrameObject *frame) noexcept
    PyFrameObject *PyFrame_GetBack(PyFrameObject *frame) noexcept
    object PyFrame_GetLocals(PyFrameObject *frame) noexcept
    object PyFrame_GetGlobals(PyFrameObject *frame) noexcept
    object PyFrame_GetBuiltins(PyFrameObject *frame) noexcept
    PyObject *PyFrame_GetGenerator(PyFrameObject *frame) noexcept
    PyObject *PyFrame_GetVar(PyFrameObject *frame, object name) except NULL
    PyObject *PyFrame_GetVarString(PyFrameObject *frame, const char *name) except NULL
    PyFrameObject *PyFrame_New(PyThreadState *tstate, PyCodeObject *code, PyObject *globals, PyObject *locals)
    bint _PyFrame_IsEntryFrame(PyFrameObject *frame) noexcept

cpdef inline bint frame_check(object frame) noexcept:
    return PyFrame_Check(frame)

cpdef inline int frame_lineno(object frame) noexcept:
    return PyFrame_GetLineNumber(<PyFrameObject *>frame)

cpdef inline int frame_lasti(object frame) noexcept:
    return PyFrame_GetLasti(<PyFrameObject *>frame)

cpdef inline object frame_code(object frame):
    return <object>PyFrame_GetCode(<PyFrameObject *>frame)

cpdef inline object frame_back(object frame):
    cdef PyFrameObject *back = PyFrame_GetBack(<PyFrameObject *>frame)
    if back == NULL:
        return None
    return <object>back

cpdef inline object frame_locals(object frame):
    return PyFrame_GetLocals(<PyFrameObject *>frame)

cpdef inline object frame_globals(object frame):
    return PyFrame_GetGlobals(<PyFrameObject *>frame)

cpdef inline object frame_builtins(object frame):
    return PyFrame_GetBuiltins(<PyFrameObject *>frame)

cpdef inline object frame_generator(object frame):
    cdef PyObject *generator = PyFrame_GetGenerator(<PyFrameObject *>frame)
    if generator == NULL:
        return None
    return <object>generator

cpdef inline object frame_var(object frame, object name):
    return <object>PyFrame_GetVar(<PyFrameObject *>frame, name)

cpdef inline object frame_var_cstr(object frame, const char *name):
    return <object>PyFrame_GetVarString(<PyFrameObject *>frame, name)

cdef inline object frame_new(PyThreadState *tstate, PyCodeObject *code, PyObject *globals, PyObject *locals):
    return <object>PyFrame_New(tstate, code, globals, locals)

cdef inline bint frame_is_entry_frame(PyFrameObject *frame) noexcept:
    return _PyFrame_IsEntryFrame(frame)
