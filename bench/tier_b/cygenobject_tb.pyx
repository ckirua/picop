# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cygenobject cimport gen_check
from types import GeneratorType
include "_sink.pxi"

cpdef bint baseline_gen_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), GeneratorType)
        tb_sink_bint(r)
    return r

cpdef bint cypy_gen_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = gen_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

