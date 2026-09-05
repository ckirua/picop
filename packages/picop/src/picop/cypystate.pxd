# cypystate.pxd
# Thread / interpreter state. cimport-only (process / GIL).
# Swap / New / Delete interpreter APIs: REJECTED for casual wrappers (fatal if misused).

from cpython.object cimport PyObject
from cpython.ref cimport Py_INCREF
from cpython.pystate cimport (
    PyGILState_STATE,
    PyThreadState,
    PyGILState_Ensure,
    PyGILState_Release,
    PyThreadState_Get,
    PyThreadState_GetDict,
)


cdef inline PyThreadState *pystate_get() noexcept:
    return PyThreadState_Get()


cdef inline object pystate_get_dict():
    cdef PyObject *p = <PyObject *>PyThreadState_GetDict()
    if p is NULL:
        return None
    cdef object obj = <object>p
    Py_INCREF(obj)
    return obj


cdef inline PyGILState_STATE pystate_gil_ensure() noexcept:
    return PyGILState_Ensure()


cdef inline void pystate_gil_release(PyGILState_STATE state) noexcept:
    PyGILState_Release(state)
