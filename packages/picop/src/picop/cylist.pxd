# cylist.pxd
# Typed ``list`` helpers. Public docs live in ``cylist.pyi``.
# ``lnew`` / ``lset`` (SET_ITEM fill): cdef — uninit / steal semantics.

from cpython.object cimport PyObject, PyObject_RichCompareBool, Py_EQ
from cpython.ref cimport Py_INCREF
from cpython.pyport cimport PY_SSIZE_T_MAX


cdef extern from "Python.h":
    void Py_DECREF(PyObject *o)
    bint PyList_Check(object p) noexcept
    bint PyList_CheckExact(object p) noexcept
    list PyList_New(Py_ssize_t len)
    Py_ssize_t PyList_Size(object list) except -1
    Py_ssize_t PyList_GET_SIZE(object list) noexcept
    PyObject* PyList_GetItem(object list, Py_ssize_t index) except NULL
    object PyList_GetItemRef(object list, Py_ssize_t index)
    PyObject* PyList_GET_ITEM(object list, Py_ssize_t i) noexcept
    int PyList_SetItem(object list, Py_ssize_t index, object item) except -1
    void PyList_SET_ITEM(object list, Py_ssize_t i, object o) noexcept
    int PyList_Insert(object list, Py_ssize_t index, object item) except -1
    int PyList_Append(object list, object item) except -1
    list PyList_GetSlice(object list, Py_ssize_t low, Py_ssize_t high)
    int PyList_SetSlice(object list, Py_ssize_t low, Py_ssize_t high, PyObject *itemlist) except -1
    int PyList_Extend(object list, object iterable) except -1
    int PyList_Clear(object list) except -1
    int PyList_Sort(object list) except -1
    int PyList_Reverse(object list) except -1
    tuple PyList_AsTuple(object list)


cdef inline bint lcheck(object p) noexcept:
    return PyList_Check(p)


cdef inline bint lcheck_exact(object p) noexcept:
    return PyList_CheckExact(p)


cdef inline list lempty():
    return PyList_New(0)


cdef inline list lnew(Py_ssize_t n):
    # Length n with NULL slots — fill via lset before Python exposure.
    return PyList_New(n)


cdef inline object lget(list l, Py_ssize_t i) noexcept:
    # No bounds check; borrowed GET_ITEM.
    return <object>PyList_GET_ITEM(l, i)


cdef inline object lget_checked(list l, Py_ssize_t i):
    # Bounds-checked borrowed GetItem (raises IndexError).
    return <object>PyList_GetItem(l, i)


cdef inline object lget_ref(list l, Py_ssize_t i):
    # Strong-ref GetItemRef (raises IndexError).
    return PyList_GetItemRef(l, i)


cdef inline Py_ssize_t llen(list l) noexcept:
    return PyList_GET_SIZE(l)


cdef inline bint leq(list a, list b):
    # Identity / len short-circuit + richcompare (same semantics as ``==``).
    if a is b:
        return True
    if PyList_GET_SIZE(a) != PyList_GET_SIZE(b):
        return False
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cdef inline Py_ssize_t lsize(object l) except -1:
    return PyList_Size(l)


cdef inline int lappend(list l, object value) except -1:
    return PyList_Append(l, value)


cdef inline int linsert(list l, Py_ssize_t i, object value) except -1:
    return PyList_Insert(l, i, value)


cdef inline int lextend(list l, object iterable) except -1:
    return PyList_Extend(l, iterable)


cdef inline int lclear(list l) except -1:
    return PyList_Clear(l)


cdef inline list lcopy(list l):
    return PyList_GetSlice(l, 0, PY_SSIZE_T_MAX)


cdef inline list lslice(list l, Py_ssize_t low, Py_ssize_t high):
    return PyList_GetSlice(l, low, high)


cdef inline int lset_slice(list l, Py_ssize_t low, Py_ssize_t high, object itemlist=None) except -1:
    # None → C NULL → delete slice (del l[low:high]).
    if itemlist is None:
        return PyList_SetSlice(l, low, high, NULL)
    return PyList_SetSlice(l, low, high, <PyObject*>itemlist)


cdef inline int lsort(list l) except -1:
    return PyList_Sort(l)


cdef inline int lreverse(list l) except -1:
    return PyList_Reverse(l)


cdef inline tuple las_tuple(list l):
    return PyList_AsTuple(l)


cdef inline int lset_item(list l, Py_ssize_t i, object value) except -1:
    # SetItem steals — INCREF so Python-held value stays valid.
    Py_INCREF(value)
    return PyList_SetItem(l, i, value)


cdef inline int lset(list l, Py_ssize_t i, object value) except -1:
    # SET_ITEM + INCREF; for filling lnew slots (does not DECREF old).
    Py_INCREF(value)
    PyList_SET_ITEM(l, i, value)
    return 0

# Wave 4 N1/N5 preferred names (0.3: soft letter/bare are cdef-only)

cpdef inline int list_append(list l, object value) except -1:
    return lappend(l, value)

cpdef inline tuple list_as_tuple(list l):
    return las_tuple(l)

cpdef inline bint list_check(object p) noexcept:
    return lcheck(p)

cpdef inline bint list_check_exact(object p) noexcept:
    return lcheck_exact(p)

cpdef inline int list_clear(list l) except -1:
    return lclear(l)

cpdef inline list list_copy(list l):
    return lcopy(l)

cpdef inline list list_empty():
    return lempty()

cpdef inline int list_extend(list l, object iterable) except -1:
    return lextend(l, iterable)

cpdef inline object list_get(list l, Py_ssize_t i) noexcept:
    return lget(l, i)

cpdef inline object list_get_checked(list l, Py_ssize_t i):
    return lget_checked(l, i)

cpdef inline object list_get_ref(list l, Py_ssize_t i):
    return lget_ref(l, i)

cpdef inline int list_insert(list l, Py_ssize_t i, object value) except -1:
    return linsert(l, i, value)

cpdef inline Py_ssize_t list_len(list l) noexcept:
    return llen(l)

cpdef inline bint list_eq(list a, list b):
    return leq(a, b)

cdef inline list list_new(Py_ssize_t n):
    return lnew(n)

cpdef inline int list_reverse(list l) except -1:
    return lreverse(l)

cdef inline int list_set(list l, Py_ssize_t i, object value) except -1:
    return lset(l, i, value)

cpdef inline int list_set_item(list l, Py_ssize_t i, object value) except -1:
    return lset_item(l, i, value)

cpdef inline int list_set_slice(list l, Py_ssize_t low, Py_ssize_t high, object itemlist=None) except -1:
    return lset_slice(l, low, high, itemlist)

cpdef inline Py_ssize_t list_size(object l) except -1:
    return lsize(l)

cpdef inline list list_slice(list l, Py_ssize_t low, Py_ssize_t high):
    return lslice(l, low, high)

cpdef inline int list_sort(list l) except -1:
    return lsort(l)

