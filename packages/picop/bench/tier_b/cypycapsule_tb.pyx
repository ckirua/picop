# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cypycapsule cimport capsule_check_exact
include "_sink.pxi"

cpdef bint baseline_capsule_check_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = type(tb_obj(p, k)).__name__ == "PyCapsule"
        tb_sink_bint(r)
    return r

cpdef bint cypy_capsule_check_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = capsule_check_exact(tb_obj(p, k))
        tb_sink_bint(r)
    return r

