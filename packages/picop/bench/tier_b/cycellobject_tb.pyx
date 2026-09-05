# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cycellobject cimport cell_check
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

