# cython: freethreading_compatible=True
# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False

from cpython.object cimport PyObject
from cpython.unicode cimport PyUnicode_AsUTF8

cdef extern from "Python.h":
    PyObject* PySys_GetObject(const char*)
    int PySys_SetObject(const char*, PyObject*) except -1
    void PySys_WriteStdout(const char*, ...)
    void PySys_WriteStderr(const char*, ...)
    void PySys_FormatStdout(const char*, ...)
    void PySys_FormatStderr(const char*, ...)
    PyObject* PySys_GetXOptions()

cdef extern from "cysys_shim.h":
    object picop_sys_get_attr(object name)
    object picop_sys_get_attr_string(const char* name)
    int picop_sys_get_optional_attr(PyObject* name, PyObject** result) except -1
    int picop_sys_get_optional_attr_string(const char* name, PyObject** result) except -1

cdef inline object _borrowed_to_owned(PyObject* p):
    if p is NULL:
        return None
    return <object>p

cdef object sys_get_object(str name):
    cdef const char* key = PyUnicode_AsUTF8(name)
    return _borrowed_to_owned(PySys_GetObject(key))

cdef object sys_get_xoptions():
    return _borrowed_to_owned(PySys_GetXOptions())

cpdef object sys_get_attr(object name):
    """Return a sys attribute by name; raise RuntimeError when absent."""
    return picop_sys_get_attr(name)

cdef object sys_get_attr_string(str name):
    cdef const char* key = PyUnicode_AsUTF8(name)
    return picop_sys_get_attr_string(key)

cdef int sys_set_object_cstr(const char* name, object value) except -1:
    return PySys_SetObject(name, <PyObject*>value if value is not None else NULL)

cdef int sys_get_optional_attr(object name, PyObject** result) except -1:
    return picop_sys_get_optional_attr(<PyObject*>name, result)

cdef int sys_get_optional_attr_string(const char* name, PyObject** result) except -1:
    return picop_sys_get_optional_attr_string(name, result)

cdef void sys_write_stdout_cstr(const char* text) noexcept:
    PySys_WriteStdout(b"%s", text)

cdef void sys_write_stderr_cstr(const char* text) noexcept:
    PySys_WriteStderr(b"%s", text)

cdef void sys_format_stdout_cstr(const char* text) noexcept:
    PySys_FormatStdout(b"%s", text)

cdef void sys_format_stderr_cstr(const char* text) noexcept:
    PySys_FormatStderr(b"%s", text)
