# cydescr.pxd
# Descriptor helpers. Public docs in ``cydescr.pyi``.
# NewWrapper needs C wrapperbase* — cdef.

from cpython.object cimport PyObject, PyTypeObject


cdef extern from "Python.h":
    int PyDescr_IsData(object descr) noexcept


cpdef inline bint descr_is_data(object descr) noexcept:
    return PyDescr_IsData(descr) != 0
