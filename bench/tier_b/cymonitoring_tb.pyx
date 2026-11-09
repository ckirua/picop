# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
"""Tier B: cymonitoring helpers vs the hand-rolled externs an extension author writes."""

from libc.stdint cimport uint8_t, uint64_t, int32_t
from cpython.object cimport PyObject
from picop.cymonitoring cimport (
    PyMonitoringState,
    PY_MONITORING_EVENT_CALL,
    PY_MONITORING_EVENT_LINE,
    PY_MONITORING_EVENT_PY_RETURN,
    fire_py_return,
    monitoring_exit_scope,
    monitoring_scope,
)
include "_sink.pxi"

# What an extension author writes without picop: the raw positional EnterScope
# and the underscore dispatch entry point that skips the `active` gate.
cdef extern from "Python.h":
    int PyMonitoring_EnterScope(PyMonitoringState *state_array, uint64_t *version,
                               const uint8_t *event_types, Py_ssize_t length) except? -1
    int PyMonitoring_ExitScope() noexcept
    int _PyMonitoring_FirePyReturnEvent(PyMonitoringState *state, PyObject *codelike,
                                        int32_t offset, PyObject *retval) except? -1

cdef PyMonitoringState states[19]
cdef uint64_t version = 0


cpdef Py_ssize_t cypy_scope_pair(object code, Py_ssize_t n):
    cdef Py_ssize_t k
    for k in range(n):
        monitoring_scope(states, &version)
        monitoring_exit_scope()
    return 1


cpdef Py_ssize_t baseline_scope_pair(object code, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef uint8_t ids[3]
    ids[0] = <uint8_t>PY_MONITORING_EVENT_LINE
    ids[1] = <uint8_t>PY_MONITORING_EVENT_PY_RETURN
    ids[2] = <uint8_t>PY_MONITORING_EVENT_CALL
    for k in range(n):
        PyMonitoring_EnterScope(states, &version, ids, 3)
        PyMonitoring_ExitScope()
    return 1


cpdef Py_ssize_t baseline_scope_pair_full(object code, Py_ssize_t n):
    # The same 18-event scope, hand-built: isolates the wrapper, not the
    # interpreter's per-id work.
    cdef Py_ssize_t k
    cdef uint8_t ids[18]
    for k in range(18):
        ids[k] = <uint8_t>k
    for k in range(n):
        PyMonitoring_EnterScope(states, &version, ids, 18)
        PyMonitoring_ExitScope()
    return 1


cpdef Py_ssize_t cypy_fire_inactive(object code, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object retval = 1
    for k in range(n):
        monitoring_scope(states, &version)
        tb_sink_ssize(fire_py_return(states, <PyObject *>code, <int32_t>k, <PyObject *>retval))
        monitoring_exit_scope()
    return 1


cpdef Py_ssize_t baseline_fire_inactive(object code, Py_ssize_t n):
    # Same scope, no gate: the dispatch entry point is called unconditionally.
    cdef Py_ssize_t k
    cdef object retval = 1
    for k in range(n):
        monitoring_scope(states, &version)
        tb_sink_ssize(_PyMonitoring_FirePyReturnEvent(&states[PY_MONITORING_EVENT_PY_RETURN],
                                                     <PyObject *>code, <int32_t>k,
                                                     <PyObject *>retval))
        monitoring_exit_scope()
    return 1


cpdef Py_ssize_t cypy_fire_active(object code, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object retval = 1
    for k in range(n):
        monitoring_scope(states, &version)
        tb_sink_ssize(fire_py_return(states, <PyObject *>code, <int32_t>k, <PyObject *>retval))
        monitoring_exit_scope()
    return 1


cpdef Py_ssize_t baseline_fire_active(object code, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object retval = 1
    for k in range(n):
        monitoring_scope(states, &version)
        tb_sink_ssize(_PyMonitoring_FirePyReturnEvent(&states[PY_MONITORING_EVENT_PY_RETURN],
                                                     <PyObject *>code, <int32_t>k,
                                                     <PyObject *>retval))
        monitoring_exit_scope()
    return 1
