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
    int picop_lazy_imports_supported()
    int picop_lazy_mode_set(int mode) except -1
    int picop_lazy_mode_get() except -1
    int picop_lazy_filter_set(PyObject* filter) except -1
    PyObject* picop_lazy_filter_get()

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

cpdef bint lazy_imports_supported():
    """Return True when the interpreter provides lazy-import controls (CPython 3.15+)."""
    return picop_lazy_imports_supported() == 1

cpdef str lazy_import_mode():
    """Return the interpreter's lazy-import mode: "normal" or "all".

    Requires CPython 3.15 or newer.
    """
    cdef int mode = picop_lazy_mode_get()
    return "all" if mode == 1 else "normal"

cpdef void set_lazy_import_mode(str mode):
    """Set the interpreter's lazy-import mode to "normal" or "all".

    Requires CPython 3.15 or newer; raises ValueError for any other value.
    """
    if mode == "all":
        picop_lazy_mode_set(1)
    elif mode == "normal":
        picop_lazy_mode_set(0)
    else:
        raise ValueError("mode must be 'normal' or 'all'")

cdef object lazy_import_filter_get():
    """Return the lazy-import filter (owned reference) or None when unset."""
    cdef PyObject* p = picop_lazy_filter_get()
    if p is NULL:
        return None
    return <object>p

cdef int lazy_import_filter_set(object filter) except -1:
    """Set the lazy-import filter (callable or None); raise ValueError if not callable."""
    return picop_lazy_filter_set(<PyObject*>filter)

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
