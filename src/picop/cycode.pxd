# cycode.pxd
# CPython code-object accessors.
# Public docs in ``cycode.pyi``.
from cpython.object cimport PyObject
cdef extern from "Python.h":
    ctypedef struct PyCodeObject:
        pass


# The shim getters return a *new* reference; declaring them as ``object`` makes
# Cython take that reference instead of incref-ing a borrowed one.
cdef extern from "cycode_shim.h":
    object cy_code_name(PyCodeObject *code) noexcept
    object cy_code_qualname(PyCodeObject *code) noexcept
    object cy_code_filename(PyCodeObject *code) noexcept
    int cy_code_firstlineno(PyCodeObject *code) noexcept
    int cy_code_argcount(PyCodeObject *code) noexcept
    int cy_code_posonlyargcount(PyCodeObject *code) noexcept
    int cy_code_kwonlyargcount(PyCodeObject *code) noexcept
    object cy_code_consts(PyCodeObject *code) noexcept
    object cy_code_names(PyCodeObject *code) noexcept

cdef extern from "cpython/code.h":
    bint PyCode_Check(object code) noexcept
    object PyCode_GetCode(PyCodeObject *code) noexcept
    object PyCode_GetVarnames(PyCodeObject *code) noexcept
    object PyCode_GetCellvars(PyCodeObject *code) noexcept
    object PyCode_GetFreevars(PyCodeObject *code) noexcept
    int PyCode_Addr2Line(PyCodeObject *code, int addr) noexcept
    int PyCode_Addr2Location(PyCodeObject *code, int addr, int *start_line, int *start_column, int *end_line, int *end_column) noexcept
    Py_ssize_t PyCode_GetNumFree(PyCodeObject *code) noexcept

cpdef inline bint code_check(object code) noexcept:
    return PyCode_Check(code)

cpdef inline object code_name(object code):
    return cy_code_name(<PyCodeObject *>code)

cpdef inline object code_qualname(object code):
    return cy_code_qualname(<PyCodeObject *>code)

cpdef inline object code_filename(object code):
    return cy_code_filename(<PyCodeObject *>code)

cpdef inline int code_firstlineno(object code) noexcept:
    return cy_code_firstlineno(<PyCodeObject *>code)

cpdef inline int code_argcount(object code) noexcept:
    return cy_code_argcount(<PyCodeObject *>code)

cpdef inline int code_posonlyargcount(object code) noexcept:
    return cy_code_posonlyargcount(<PyCodeObject *>code)

cpdef inline int code_kwonlyargcount(object code) noexcept:
    return cy_code_kwonlyargcount(<PyCodeObject *>code)

cpdef inline object code_consts(object code):
    return cy_code_consts(<PyCodeObject *>code)

cpdef inline object code_names(object code):
    return cy_code_names(<PyCodeObject *>code)

cpdef inline object code_code(object code):
    return PyCode_GetCode(<PyCodeObject *>code)

cpdef inline object code_varnames(object code):
    return PyCode_GetVarnames(<PyCodeObject *>code)

cpdef inline object code_cellvars(object code):
    return PyCode_GetCellvars(<PyCodeObject *>code)

cpdef inline object code_freevars(object code):
    return PyCode_GetFreevars(<PyCodeObject *>code)

cpdef inline int code_addr2line(object code, int addr) noexcept:
    return PyCode_Addr2Line(<PyCodeObject *>code, addr)

cdef inline Py_ssize_t code_num_free(PyCodeObject *code) noexcept:
    return PyCode_GetNumFree(code)

cdef inline tuple code_addr2_location(PyCodeObject *code, int addr):
    cdef int start_line
    cdef int start_column
    cdef int end_line
    cdef int end_column
    PyCode_Addr2Location(code, addr, &start_line, &start_column, &end_line, &end_column)
    return (start_line, start_column, end_line, end_column)
