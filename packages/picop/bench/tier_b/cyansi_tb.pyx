# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cyansi cimport ansi_fg8, ansi_bg8, ansi_bold
include "_sink.pxi"

cpdef str baseline_fg8(int code, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef str r
    cdef int c
    for k in range(n):
        c = code
        tb_sink_ssize(c ^ (k & 0))
        r = f"\x1b[{c}m"
        tb_sink_obj(r)
    return r

cpdef str cypy_fg8(int code, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef str r
    cdef int c
    for k in range(n):
        c = code
        tb_sink_ssize(c ^ (k & 0))
        r = ansi_fg8(c)
        tb_sink_obj(r)
    return r

cpdef str baseline_bg8(int code, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef str r
    cdef int c
    for k in range(n):
        c = code
        tb_sink_ssize(c ^ (k & 0))
        r = f"\x1b[{c}m"
        tb_sink_obj(r)
    return r

cpdef str cypy_bg8(int code, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef str r
    cdef int c
    for k in range(n):
        c = code
        tb_sink_ssize(c ^ (k & 0))
        r = ansi_bg8(c)
        tb_sink_obj(r)
    return r

cpdef str baseline_bold(bint on, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef str r
    for k in range(n):
        tb_sink_bint(on)
        tb_sink_ssize(k & 0)
        r = "\x1b[1m" if on else "\x1b[0m"
        tb_sink_obj(r)
    return r

cpdef str cypy_bold(bint on, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef str r
    for k in range(n):
        tb_sink_ssize(k & 0)
        r = ansi_bold(on)
        tb_sink_obj(r)
    return r

