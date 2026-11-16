# cycellobject.pxd
# Closure cell helpers. Public docs in ``cycellobject.pyi``.
# GET/SET macros: cdef unchecked.

from cpython.object cimport PyObject, PyObject_RichCompareBool, Py_EQ
import cython


cdef extern from "cycellobject_shim.h":
    object cy_cell_swap(PyObject *cell, PyObject *value)
    object cy_cell_empty()

cpdef inline object cell_empty():
    return cy_cell_empty()


cpdef inline object cell_swap(object cell, object value):
    if not PyCell_Check(cell):
        raise TypeError("expected a cell object")
    return cy_cell_swap(<PyObject *>cell, <PyObject *>value)


cdef extern from "Python.h":
    bint PyCell_Check(object ob) noexcept
    object PyCell_New(object ob)
    # ``PyCell_GET`` is the macro form: it returns a *borrowed* pointer, so it
    # must be promoted with an ``<object>`` cast, never declared as ``object``.
    PyObject *PyCell_GET(PyObject *cell) noexcept
    int PyCell_Set(object cell, object value) except -1
    void PyCell_SET(object cell, object value) noexcept


cpdef inline bint cell_check(object ob) noexcept:
    return PyCell_Check(ob)


cpdef inline object cell_new(object ob):
    return PyCell_New(ob)


cpdef inline object cell_get(object cell):
    # ``PyCell_Get`` returns NULL for an empty cell *without setting an
    # exception* (CPython 3.14/3.15), so an ``object``-typed extern wrapper
    # would raise with no exception object and crash in the traceback
    # machinery. Read the borrowed pointer and raise explicitly instead.
    cdef PyObject *ref
    with cython.critical_section(cell):
        ref = PyCell_GET(<PyObject *>cell)
        if ref == NULL:
            raise ValueError("cell is empty")
        return <object>ref


cpdef inline int cell_set(object cell, object value) except -1:
    return PyCell_Set(cell, value)


cdef inline bint celleq(object a, object b) except -1:
    # Cell equality is content equality (CPython ``cell_richcompare``) —
    # empty↔empty True; equal contents True; not identity. Soft ``celleq``.
    # Callers should pass cell objects. Not on ``hot`` — validate win first.
    if a is b:
        return True
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cpdef inline bint cell_eq(object a, object b) except -1:
    return celleq(a, b)


cdef inline object cell_get_unchecked(object cell):
    # No type check — UB if not a cell. The caller must satisfy the cell
    # type precondition; keep the borrowed load and its promotion atomic.
    cdef PyObject *res
    with cython.critical_section(cell):
        res = PyCell_GET(<PyObject *>cell)
        return <object>res


cdef inline void cell_set_unchecked(object cell, object value) noexcept:
    # No refcount adjustment/type check; caller retains the documented
    # reference-transfer responsibility.
    with cython.critical_section(cell):
        PyCell_SET(cell, value)
