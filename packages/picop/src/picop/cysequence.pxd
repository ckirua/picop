# cysequence.pxd
# Sequence protocol helpers. Public docs in ``cysequence.pyi``.
# Fast/ITEM macros and Fast_ITEMS pointer: cdef.

from cpython.object cimport PyObject, PyObject_RichCompareBool, Py_EQ


cdef extern from "Python.h":
    bint PySequence_Check(object o) noexcept
    Py_ssize_t PySequence_Size(object o) except -1
    Py_ssize_t PySequence_Length(object o) except -1
    object PySequence_Concat(object o1, object o2)
    object PySequence_Repeat(object o, Py_ssize_t count)
    object PySequence_InPlaceConcat(object o1, object o2)
    object PySequence_InPlaceRepeat(object o, Py_ssize_t count)
    object PySequence_GetItem(object o, Py_ssize_t i)
    object PySequence_GetSlice(object o, Py_ssize_t i1, Py_ssize_t i2)
    int PySequence_SetItem(object o, Py_ssize_t i, object v) except -1
    int PySequence_DelItem(object o, Py_ssize_t i) except -1
    int PySequence_SetSlice(object o, Py_ssize_t i1, Py_ssize_t i2, object v) except -1
    int PySequence_DelSlice(object o, Py_ssize_t i1, Py_ssize_t i2) except -1
    int PySequence_Count(object o, object value) except -1
    int PySequence_Contains(object o, object value) except -1
    Py_ssize_t PySequence_Index(object o, object value) except -1
    object PySequence_List(object o)
    object PySequence_Tuple(object o)
    object PySequence_Fast(object o, const char *m)
    PyObject *PySequence_Fast_GET_ITEM(object o, Py_ssize_t i) noexcept
    PyObject **PySequence_Fast_ITEMS(object o) noexcept
    object PySequence_ITEM(object o, Py_ssize_t i)
    Py_ssize_t PySequence_Fast_GET_SIZE(object o) noexcept


cdef inline bint sqcheck(object o) noexcept:
    return PySequence_Check(o)


cdef inline bint sqeq(object a, object b):
    # Identity / size short-circuit + richcompare (same semantics as ``==``).
    # Soft name ``sqeq``; prefer typed ``list_eq`` / ``tuple_eq`` when known.
    if a is b:
        return True
    if PySequence_Size(a) != PySequence_Size(b):
        return False
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cdef inline Py_ssize_t sqsize(object o) except -1:
    return PySequence_Size(o)


cdef inline Py_ssize_t sqlen(object o) except -1:
    # Alias of Size (cheap sibling).
    return PySequence_Length(o)


cdef inline object sqconcat(object o1, object o2):
    return PySequence_Concat(o1, o2)


cdef inline object sqrepeat(object o, Py_ssize_t count):
    return PySequence_Repeat(o, count)


cdef inline object sqinplace_concat(object o1, object o2):
    return PySequence_InPlaceConcat(o1, o2)


cdef inline object sqinplace_repeat(object o, Py_ssize_t count):
    return PySequence_InPlaceRepeat(o, count)


cdef inline object sqget(object o, Py_ssize_t i):
    return PySequence_GetItem(o, i)


cdef inline object sqslice(object o, Py_ssize_t i1, Py_ssize_t i2):
    return PySequence_GetSlice(o, i1, i2)


cdef inline int sqset(object o, Py_ssize_t i, object v) except -1:
    return PySequence_SetItem(o, i, v)


cdef inline int sqdel(object o, Py_ssize_t i) except -1:
    return PySequence_DelItem(o, i)


cdef inline int sqset_slice(object o, Py_ssize_t i1, Py_ssize_t i2, object v) except -1:
    return PySequence_SetSlice(o, i1, i2, v)


cdef inline int sqdel_slice(object o, Py_ssize_t i1, Py_ssize_t i2) except -1:
    return PySequence_DelSlice(o, i1, i2)


cdef inline int sqcount(object o, object value) except -1:
    return PySequence_Count(o, value)


cdef inline bint sqcontains(object o, object value) except -1:
    return PySequence_Contains(o, value)


cdef inline Py_ssize_t sqindex(object o, object value) except -1:
    return PySequence_Index(o, value)


cdef inline list sqlist(object o):
    return <list>PySequence_List(o)


cdef inline tuple sqtuple(object o):
    return <tuple>PySequence_Tuple(o)


cdef inline object sqfast(object o, const char *msg):
    # Returns list/tuple as-is or new tuple; msg for TypeError.
    return PySequence_Fast(o, msg)


cdef inline object sqfast_get(object o, Py_ssize_t i) noexcept:
    # Borrowed; o must be from sqfast / list / tuple; no bounds check.
    return <object>PySequence_Fast_GET_ITEM(o, i)


cdef inline PyObject **sqfast_items(object o) noexcept:
    return PySequence_Fast_ITEMS(o)


cdef inline object sqitem(object o, Py_ssize_t i):
    # Macro GetItem without Check / negative-index adjust.
    return PySequence_ITEM(o, i)


cdef inline Py_ssize_t sqfast_size(object o) noexcept:
    return PySequence_Fast_GET_SIZE(o)

# Wave 4 N1/N5 preferred names (0.3: soft letter/bare are cdef-only)

cpdef inline bint seq_check(object o) noexcept:
    return sqcheck(o)

cpdef inline object seq_concat(object o1, object o2):
    return sqconcat(o1, o2)

cpdef inline bint seq_contains(object o, object value) except -1:
    return sqcontains(o, value)

cpdef inline int seq_count(object o, object value) except -1:
    return sqcount(o, value)

cpdef inline bint seq_eq(object a, object b):
    return sqeq(a, b)

cpdef inline int seq_del(object o, Py_ssize_t i) except -1:
    return sqdel(o, i)

cpdef inline int seq_del_slice(object o, Py_ssize_t i1, Py_ssize_t i2) except -1:
    return sqdel_slice(o, i1, i2)

cdef inline object seq_fast(object o, const char *msg):
    return sqfast(o, msg)

cdef inline object seq_fast_get(object o, Py_ssize_t i) noexcept:
    return sqfast_get(o, i)

cdef inline Py_ssize_t seq_fast_size(object o) noexcept:
    return sqfast_size(o)

cpdef inline object seq_get(object o, Py_ssize_t i):
    return sqget(o, i)

cpdef inline Py_ssize_t seq_index(object o, object value) except -1:
    return sqindex(o, value)

cpdef inline object seq_inplace_concat(object o1, object o2):
    return sqinplace_concat(o1, o2)

cpdef inline object seq_inplace_repeat(object o, Py_ssize_t count):
    return sqinplace_repeat(o, count)

cdef inline object seq_item(object o, Py_ssize_t i):
    return sqitem(o, i)

cpdef inline Py_ssize_t seq_len(object o) except -1:
    return sqlen(o)

cpdef inline list seq_list(object o):
    return sqlist(o)

cpdef inline object seq_repeat(object o, Py_ssize_t count):
    return sqrepeat(o, count)

cpdef inline int seq_set(object o, Py_ssize_t i, object v) except -1:
    return sqset(o, i, v)

cpdef inline int seq_set_slice(object o, Py_ssize_t i1, Py_ssize_t i2, object v) except -1:
    return sqset_slice(o, i1, i2, v)

cpdef inline Py_ssize_t seq_size(object o) except -1:
    return sqsize(o)

cpdef inline object seq_slice(object o, Py_ssize_t i1, Py_ssize_t i2):
    return sqslice(o, i1, i2)

cpdef inline tuple seq_tuple(object o):
    return sqtuple(o)

