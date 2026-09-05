# cyerr.pxd
# Thin ``PyErr_*`` slice for extension code (cimport-only). Requires GIL.
# Full ``cpython.exc`` remainder deferred / out of current slice.

from cpython.exc cimport (
    PyErr_Clear,
    PyErr_ExceptionMatches,
    PyErr_Fetch,
    PyErr_NoMemory,
    PyErr_Occurred,
    PyErr_Restore,
    PyErr_SetNone,
    PyErr_SetObject,
    PyErr_SetString,
)
from cpython.object cimport PyObject


cdef inline void err_clear() noexcept:
    PyErr_Clear()


cdef inline bint err_occurred() noexcept:
    return PyErr_Occurred() != NULL


cdef inline bint err_exception_matches(object exc) noexcept:
    # Only valid when an exception is set (else UB).
    return PyErr_ExceptionMatches(exc)


cdef inline void err_set_string(object exc, const char *message) noexcept:
    PyErr_SetString(exc, message)


cdef inline void err_set_object(object exc, object value) noexcept:
    PyErr_SetObject(exc, value)


cdef inline void err_set_none(object exc) noexcept:
    PyErr_SetNone(exc)


cdef inline PyObject *err_no_memory() noexcept:
    return PyErr_NoMemory()


cdef inline void err_fetch(PyObject **ptype, PyObject **pvalue, PyObject **ptraceback) noexcept:
    # Steals the thread error indicator into the three out-params (new refs).
    PyErr_Fetch(ptype, pvalue, ptraceback)


cdef inline void err_restore(PyObject *type, PyObject *value, PyObject *traceback) noexcept:
    # Steals the three refs into the thread error indicator.
    PyErr_Restore(type, value, traceback)
