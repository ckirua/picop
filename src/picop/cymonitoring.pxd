# cymonitoring.pxd
# CPython event-monitoring plumbing (PEP 670, C API in 3.13+). Cimport only:
# `sys.monitoring` owns registration; this module only lets an extension
# *emit* the events for code it executes itself.
#
# Pattern for an extension that emulates Python execution:
#   cdef PyMonitoringState states[19]      # one slot per event id
#   cdef unsigned long long version = 0
#   monitoring_scope(states, &version)     # once per lexical scope
#   if monitoring_active(states, PY_MONITORING_EVENT_LINE):
#       fire_line(states, codelike, offset, lineno)
#   monitoring_exit_scope()

from libc.stdint cimport uint8_t, uint64_t, int32_t
from cpython.object cimport PyObject

cdef extern from "cymonitoring_shim.h":
    # 18 event ids (0..17); the deprecated PY_MONITORING_EVENT_BRANCH (18) is
    # excluded, but the state array still needs 19 slots.
    const uint8_t *cypy_monitoring_all_events
    int PICOP_MONITORING_SCOPE_EVENT_COUNT
    int PICOP_MONITORING_STATE_SLOTS

cdef extern from "Python.h" nogil:
    # Event ids. `PY_MONITORING_EVENT_BRANCH` (18) is deprecated in 3.14 and is
    # deliberately not declared; use the left/right pair.
    int PY_MONITORING_EVENT_PY_START
    int PY_MONITORING_EVENT_PY_RESUME
    int PY_MONITORING_EVENT_PY_RETURN
    int PY_MONITORING_EVENT_PY_YIELD
    int PY_MONITORING_EVENT_CALL
    int PY_MONITORING_EVENT_LINE
    int PY_MONITORING_EVENT_INSTRUCTION
    int PY_MONITORING_EVENT_JUMP
    int PY_MONITORING_EVENT_BRANCH_LEFT
    int PY_MONITORING_EVENT_BRANCH_RIGHT
    int PY_MONITORING_EVENT_STOP_ITERATION
    int PY_MONITORING_EVENT_RAISE
    int PY_MONITORING_EVENT_EXCEPTION_HANDLED
    int PY_MONITORING_EVENT_PY_UNWIND
    int PY_MONITORING_EVENT_PY_THROW
    int PY_MONITORING_EVENT_RERAISE
    int PY_MONITORING_EVENT_C_RETURN
    int PY_MONITORING_EVENT_C_RAISE

    # Contents are "not part of the public API"; `active` is a tool bitmask,
    # not a bool. Declared so extensions can size a stack-local array.
    ctypedef struct PyMonitoringState:
        unsigned char active
        unsigned char opaque

    int PyMonitoring_EnterScope(PyMonitoringState *state_array, uint64_t *version,
                               const uint8_t *event_types, Py_ssize_t length) except? -1
    int PyMonitoring_ExitScope()

    int PyMonitoring_FirePyStartEvent(PyMonitoringState *state, PyObject *codelike, int32_t offset) except? -1
    int PyMonitoring_FirePyResumeEvent(PyMonitoringState *state, PyObject *codelike, int32_t offset) except? -1
    int PyMonitoring_FirePyReturnEvent(PyMonitoringState *state, PyObject *codelike, int32_t offset, PyObject *retval) except? -1
    int PyMonitoring_FirePyYieldEvent(PyMonitoringState *state, PyObject *codelike, int32_t offset, PyObject *retval) except? -1
    int PyMonitoring_FireCallEvent(PyMonitoringState *state, PyObject *codelike, int32_t offset, PyObject *callable, PyObject *arg0) except? -1
    int PyMonitoring_FireLineEvent(PyMonitoringState *state, PyObject *codelike, int32_t offset, int lineno) except? -1
    int PyMonitoring_FireJumpEvent(PyMonitoringState *state, PyObject *codelike, int32_t offset, PyObject *target_offset) except? -1
    int PyMonitoring_FireBranchLeftEvent(PyMonitoringState *state, PyObject *codelike, int32_t offset, PyObject *target_offset) except? -1
    int PyMonitoring_FireBranchRightEvent(PyMonitoringState *state, PyObject *codelike, int32_t offset, PyObject *target_offset) except? -1
    int PyMonitoring_FireCReturnEvent(PyMonitoringState *state, PyObject *codelike, int32_t offset, PyObject *retval) except? -1
    int PyMonitoring_FirePyThrowEvent(PyMonitoringState *state, PyObject *codelike, int32_t offset) except? -1
    int PyMonitoring_FireRaiseEvent(PyMonitoringState *state, PyObject *codelike, int32_t offset) except? -1
    int PyMonitoring_FireReraiseEvent(PyMonitoringState *state, PyObject *codelike, int32_t offset) except? -1
    int PyMonitoring_FireExceptionHandledEvent(PyMonitoringState *state, PyObject *codelike, int32_t offset) except? -1
    int PyMonitoring_FireCRaiseEvent(PyMonitoringState *state, PyObject *codelike, int32_t offset) except? -1
    int PyMonitoring_FirePyUnwindEvent(PyMonitoringState *state, PyObject *codelike, int32_t offset) except? -1
    int PyMonitoring_FireStopIterationEvent(PyMonitoringState *state, PyObject *codelike, int32_t offset, PyObject *value) except? -1


cdef inline int monitoring_scope(PyMonitoringState *states, uint64_t *version) except? -1:
    """Enter a scope over the 18 live PEP 670 events.

    `states` must be a stack array of PICOP_MONITORING_STATE_SLOTS (19)
    elements; the version counter lets the interpreter reuse the computed
    active masks across scopes.
    """
    return PyMonitoring_EnterScope(states, version, cypy_monitoring_all_events,
                                   PICOP_MONITORING_SCOPE_EVENT_COUNT)


cdef inline int monitoring_exit_scope() noexcept nogil:
    return PyMonitoring_ExitScope()


cdef inline bint monitoring_active(PyMonitoringState *states, int event) noexcept nogil:
    return states[event].active != 0


cdef inline bint monitoring_is_instrumented(int event) noexcept nogil:
    # Mirrors PY_MONITORING_IS_INSTRUMENTED_EVENT: the bytecode-instrumented
    # (local) events, i.e. PY_START .. STOP_ITERATION.
    return (event >= PY_MONITORING_EVENT_PY_START) and (event <= PY_MONITORING_EVENT_STOP_ITERATION)


cdef inline int fire_py_start(PyMonitoringState *states, PyObject *codelike, int32_t offset) except? -1:
    return PyMonitoring_FirePyStartEvent(&states[PY_MONITORING_EVENT_PY_START], codelike, offset)


cdef inline int fire_py_resume(PyMonitoringState *states, PyObject *codelike, int32_t offset) except? -1:
    return PyMonitoring_FirePyResumeEvent(&states[PY_MONITORING_EVENT_PY_RESUME], codelike, offset)


cdef inline int fire_py_return(PyMonitoringState *states, PyObject *codelike, int32_t offset, PyObject *retval) except? -1:
    return PyMonitoring_FirePyReturnEvent(&states[PY_MONITORING_EVENT_PY_RETURN], codelike, offset, retval)


cdef inline int fire_py_yield(PyMonitoringState *states, PyObject *codelike, int32_t offset, PyObject *retval) except? -1:
    return PyMonitoring_FirePyYieldEvent(&states[PY_MONITORING_EVENT_PY_YIELD], codelike, offset, retval)


cdef inline int fire_call(PyMonitoringState *states, PyObject *codelike, int32_t offset, PyObject *callable, PyObject *arg0) except? -1:
    return PyMonitoring_FireCallEvent(&states[PY_MONITORING_EVENT_CALL], codelike, offset, callable, arg0)


cdef inline int fire_line(PyMonitoringState *states, PyObject *codelike, int32_t offset, int lineno) except? -1:
    return PyMonitoring_FireLineEvent(&states[PY_MONITORING_EVENT_LINE], codelike, offset, lineno)


cdef inline int fire_jump(PyMonitoringState *states, PyObject *codelike, int32_t offset, PyObject *target_offset) except? -1:
    return PyMonitoring_FireJumpEvent(&states[PY_MONITORING_EVENT_JUMP], codelike, offset, target_offset)


cdef inline int fire_branch_left(PyMonitoringState *states, PyObject *codelike, int32_t offset, PyObject *target_offset) except? -1:
    return PyMonitoring_FireBranchLeftEvent(&states[PY_MONITORING_EVENT_BRANCH_LEFT], codelike, offset, target_offset)


cdef inline int fire_branch_right(PyMonitoringState *states, PyObject *codelike, int32_t offset, PyObject *target_offset) except? -1:
    return PyMonitoring_FireBranchRightEvent(&states[PY_MONITORING_EVENT_BRANCH_RIGHT], codelike, offset, target_offset)


cdef inline int fire_c_return(PyMonitoringState *states, PyObject *codelike, int32_t offset, PyObject *retval) except? -1:
    return PyMonitoring_FireCReturnEvent(&states[PY_MONITORING_EVENT_C_RETURN], codelike, offset, retval)


cdef inline int fire_py_throw(PyMonitoringState *states, PyObject *codelike, int32_t offset) except? -1:
    return PyMonitoring_FirePyThrowEvent(&states[PY_MONITORING_EVENT_PY_THROW], codelike, offset)


cdef inline int fire_raise(PyMonitoringState *states, PyObject *codelike, int32_t offset) except? -1:
    return PyMonitoring_FireRaiseEvent(&states[PY_MONITORING_EVENT_RAISE], codelike, offset)


cdef inline int fire_reraise(PyMonitoringState *states, PyObject *codelike, int32_t offset) except? -1:
    return PyMonitoring_FireReraiseEvent(&states[PY_MONITORING_EVENT_RERAISE], codelike, offset)


cdef inline int fire_exception_handled(PyMonitoringState *states, PyObject *codelike, int32_t offset) except? -1:
    return PyMonitoring_FireExceptionHandledEvent(&states[PY_MONITORING_EVENT_EXCEPTION_HANDLED], codelike, offset)


cdef inline int fire_c_raise(PyMonitoringState *states, PyObject *codelike, int32_t offset) except? -1:
    return PyMonitoring_FireCRaiseEvent(&states[PY_MONITORING_EVENT_C_RAISE], codelike, offset)


cdef inline int fire_py_unwind(PyMonitoringState *states, PyObject *codelike, int32_t offset) except? -1:
    return PyMonitoring_FirePyUnwindEvent(&states[PY_MONITORING_EVENT_PY_UNWIND], codelike, offset)


cdef inline int fire_stop_iteration(PyMonitoringState *states, PyObject *codelike, int32_t offset, PyObject *value) except? -1:
    return PyMonitoring_FireStopIterationEvent(&states[PY_MONITORING_EVENT_STOP_ITERATION], codelike, offset, value)
