# cytraceback.pxd
# CPython traceback-object accessors.
# Public docs in ``cytraceback.pyi``.
from cpython.object cimport PyObject

cdef extern from "Python.h":
    bint PyTraceBack_Check(object tb) noexcept

cdef extern from "cytraceback_shim.h":
    object cy_tb_next(PyObject *tb) noexcept
    PyObject *cy_tb_next_raw(PyObject *tb) noexcept
    object cy_tb_frame(PyObject *tb) noexcept
    int cy_tb_lineno(PyObject *tb) noexcept
    int cy_tb_lasti(PyObject *tb) noexcept
    Py_ssize_t cy_tb_depth(PyObject *tb) noexcept

cpdef inline bint tb_check(object tb) noexcept:
    return PyTraceBack_Check(tb)

cpdef inline object tb_next(object tb):
    return cy_tb_next(<PyObject *>tb)

cdef inline PyObject *tb_next_borrow(object tb) noexcept:
    return cy_tb_next_raw(<PyObject *>tb)

cpdef inline object tb_frame(object tb):
    return cy_tb_frame(<PyObject *>tb)

cpdef inline int tb_lineno(object tb) noexcept:
    return cy_tb_lineno(<PyObject *>tb)

cpdef inline int tb_lasti(object tb) noexcept:
    return cy_tb_lasti(<PyObject *>tb)

cpdef inline Py_ssize_t tb_depth(object tb) noexcept:
    return cy_tb_depth(<PyObject *>tb)
