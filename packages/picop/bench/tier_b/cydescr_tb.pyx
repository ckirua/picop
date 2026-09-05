# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cydescr cimport descr_is_data
include "_sink.pxi"

cpdef bint baseline_descr_is_data(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        # Python-level: data descriptors have __set__ or __delete__
        d = tb_obj(p, k)
        r = hasattr(type(d), "__set__") or hasattr(type(d), "__delete__")
        tb_sink_bint(r)
    return r

cpdef bint cypy_descr_is_data(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = descr_is_data(tb_obj(p, k))
        tb_sink_bint(r)
    return r

