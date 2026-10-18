# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cydatetime cimport dt_date_check
from cpython.datetime cimport import_datetime, date
include "_sink.pxi"

import_datetime()


cpdef bint baseline_dt_date_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), date)
        tb_sink_bint(r)
    return r


cpdef bint cypy_dt_date_check(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = dt_date_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r
