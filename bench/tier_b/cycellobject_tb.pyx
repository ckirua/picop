# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from picop.cycellobject cimport cell_check, cell_swap, cell_get, cell_set
from cpython.object cimport PyObject
include "_sink.pxi"

cpdef bint baseline_cell_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = type(tb_obj(p, k)).__name__ == "cell"
        tb_sink_bint(r)
    return r

cpdef bint cypy_cell_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = cell_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef object baseline_cell_swap(object cell, object value, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object old
    for k in range(n):
        old = cell_get(cell)
        cell_set(cell, value)
        tb_sink_obj(old)
    return old

cpdef object cypy_cell_swap(object cell, object value, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object old
    for k in range(n):
        old = cell_swap(cell, value)
        tb_sink_obj(old)
    return old
