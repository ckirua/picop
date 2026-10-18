# cyref.pxd
# Reference-count helpers. cimport-only — unsafe from Python (can free live objects).
# Prefer these thin aliases from Cython; do not expose as ``cpdef``.

from cpython.object cimport PyObject
from cpython.ref cimport (
    Py_CLEAR,
    Py_DECREF,
    Py_INCREF,
    Py_REFCNT,
    Py_XDECREF,
    Py_XINCREF,
)


cdef extern from "Python.h":
    int PyUnstable_Object_EnableDeferredRefcount(object o) noexcept
    int PyUnstable_Object_IsUniqueReferencedTemporary(object o) noexcept
    int PyUnstable_IsImmortal(object o) noexcept
    void PyUnstable_EnableTryIncRef(object o) noexcept
    bint PyUnstable_TryIncRef(PyObject *o) noexcept
    int PyUnstable_Object_IsUniquelyReferenced(object o) noexcept


cdef inline void ref_incref(object o) noexcept:
    Py_INCREF(o)


cdef inline void ref_xincref(PyObject *o) noexcept:
    Py_XINCREF(o)


cdef inline void ref_decref(object o) noexcept:
    # May invoke arbitrary ``__del__``; caller must ensure consistent state.
    Py_DECREF(o)


cdef inline void ref_xdecref(PyObject *o) noexcept:
    Py_XDECREF(o)


cdef inline Py_ssize_t ref_refcnt(object o) noexcept:
    # Immortal objects report a huge count — do not treat as precise.
    return Py_REFCNT(o)


cdef inline int ref_enable_deferred(object o) noexcept:
    return PyUnstable_Object_EnableDeferredRefcount(o)


cdef inline int ref_is_unique_temporary(object o) noexcept:
    return PyUnstable_Object_IsUniqueReferencedTemporary(o)


cdef inline int ref_is_immortal(object o) noexcept:
    return PyUnstable_IsImmortal(o)


cdef inline void ref_enable_try_incref(object o) noexcept:
    PyUnstable_EnableTryIncRef(o)


cdef inline bint ref_try_incref(PyObject *o) noexcept:
    return PyUnstable_TryIncRef(o)


cdef inline int ref_is_uniquely_referenced(object o) noexcept:
    return PyUnstable_Object_IsUniquelyReferenced(o)
