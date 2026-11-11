# cydescr.pxd
# Descriptor helpers. Public docs in ``cydescr.pyi``.
# cimport-only constructors and member access require caller-owned static tables/addresses.

from cpython.object cimport PyTypeObject


cdef extern from "descrobject.h":
    int PyDescr_IsData(object descr) noexcept
    object PyDescr_NAME(object descr) noexcept
    PyTypeObject *PyDescr_TYPE(object descr) noexcept
    PyTypeObject PyMethodDescr_Type
    PyTypeObject PyClassMethodDescr_Type
    PyTypeObject PyMemberDescr_Type
    PyTypeObject PyGetSetDescr_Type
    PyTypeObject PyWrapperDescr_Type

cdef extern from "Python.h":
    int PyObject_TypeCheck(object obj, PyTypeObject *type) noexcept

cdef inline bint _is_descr(object descr) noexcept:
    return (PyObject_TypeCheck(descr, &PyMethodDescr_Type) or
            PyObject_TypeCheck(descr, &PyClassMethodDescr_Type) or
            PyObject_TypeCheck(descr, &PyMemberDescr_Type) or
            PyObject_TypeCheck(descr, &PyGetSetDescr_Type) or
            PyObject_TypeCheck(descr, &PyWrapperDescr_Type))

cdef extern from "descrobject.h":
    object PyDescr_NewMethod(PyTypeObject *, void *) # static table lifetime required
    object PyDescr_NewClassMethod(PyTypeObject *, void *)
    object PyDescr_NewMember(PyTypeObject *, void *)
    object PyDescr_NewGetSet(PyTypeObject *, void *)
    object PyMember_GetOne(const char *, void *)
    int PyMember_SetOne(char *, void *, object)

cpdef inline object descr_name(object descr):
    if not _is_descr(descr):
        raise TypeError("expected a CPython descriptor")
    return PyDescr_NAME(descr)

cpdef inline object descr_objclass(object descr):
    if not _is_descr(descr):
        raise TypeError("expected a CPython descriptor")
    return <object>PyDescr_TYPE(descr)

cpdef inline bint descr_is_data(object descr) noexcept:
    return PyDescr_IsData(descr) != 0

