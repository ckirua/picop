# cython: language_level=3

from cpython.buffer cimport Py_buffer
from cpython.object cimport PyObject, PyTypeObject
from .cypicklebuf cimport pickle_buffer_get_buffer

cdef extern from "cypicklebuf_shim.h":
    PyObject* picop_pickle_buffer_from_object(PyObject*) except NULL
    int picop_pickle_buffer_release(PyObject*) except -1
    int picop_pickle_buffer_check(PyObject*) except -1
    const Py_buffer* picop_pickle_buffer_get_buffer(PyObject*) except? NULL
    PyTypeObject* picop_pickle_buffer_type() except NULL


cpdef object pickle_buffer_from_object(object obj):
    """Create a PickleBuffer from a buffer-protocol object."""
    return <object>picop_pickle_buffer_from_object(<PyObject*>obj)

cpdef void pickle_buffer_release(object obj):
    """Release the exported buffer held by a PickleBuffer."""
    if not picop_pickle_buffer_check(<PyObject*>obj):
        raise TypeError("expected a PickleBuffer")
    picop_pickle_buffer_release(<PyObject*>obj)

cpdef bint pickle_buffer_check(object obj):
    """Return whether obj is exactly a PickleBuffer instance."""
    return picop_pickle_buffer_check(<PyObject*>obj) != 0

cpdef object pickle_buffer_type():
    """Return the PickleBuffer type object."""
    return <object><PyObject*>picop_pickle_buffer_type()

cdef const Py_buffer* pickle_buffer_get_buffer(object obj) except? NULL:
    if not picop_pickle_buffer_check(<PyObject*>obj):
        raise TypeError("expected a PickleBuffer")
    return picop_pickle_buffer_get_buffer(<PyObject*>obj)
