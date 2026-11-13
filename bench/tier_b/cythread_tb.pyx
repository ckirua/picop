# cython: language_level=3, boundscheck=False, wraparound=False
"""Tier B loops: interpreter-guard helpers vs raw GILState pair."""

cdef extern from "Python.h":
    int PyGILState_Ensure()
    void PyGILState_Release(int state)
from picop.cythread cimport guards_enabled, guard_from_current, guard_close, threadstate_ensure, threadstate_release

include "_sink.pxi"


cpdef object baseline_gil_loop(Py_ssize_t n):
    cdef Py_ssize_t k
    cdef int st
    for k in range(n):
        st = PyGILState_Ensure()
        PyGILState_Release(st)
        tb_sink_ssize(st)
    return None


cpdef object cypy_guard_loop(Py_ssize_t n):
    cdef Py_ssize_t k
    cdef void *g
    if not guards_enabled():
        return None
    for k in range(n):
        g = guard_from_current()
        guard_close(g)
        tb_sink_ssize(k)
    return None


cpdef object cypy_ensure_loop(Py_ssize_t n):
    cdef Py_ssize_t k
    cdef void *g
    cdef void *t
    if not guards_enabled():
        return None
    g = guard_from_current()
    for k in range(n):
        t = threadstate_ensure(g)
        threadstate_release(t)
        tb_sink_ssize(k)
    guard_close(g)
    return None
