# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cymodule cimport mod_check
from types import ModuleType
include "_sink.pxi"

cpdef bint baseline_mod_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), ModuleType)
        tb_sink_bint(r)
    return r

cpdef bint cypy_mod_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = mod_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

