# cymapping.pxd
# Mapping protocol helpers. Public docs in ``cymapping.pyi``.

from cpython.object cimport PyObject_RichCompareBool, Py_EQ


cdef extern from "Python.h":
    bint PyMapping_Check(object o) noexcept
    Py_ssize_t PyMapping_Length(object o) except -1
    int PyMapping_DelItemString(object o, const char *key) except -1
    int PyMapping_DelItem(object o, object key) except -1
    bint PyMapping_HasKeyString(object o, const char *key) noexcept
    bint PyMapping_HasKey(object o, object key) noexcept
    object PyMapping_Keys(object o)
    object PyMapping_Values(object o)
    object PyMapping_Items(object o)
    object PyMapping_GetItemString(object o, const char *key)
    int PyMapping_SetItemString(object o, const char *key, object v) except -1


cdef inline bint mapeq(object a, object b):
    # Identity / size short-circuit + richcompare (same semantics as ``==``).
    # Soft name ``mapeq``; prefer typed ``dict_eq`` when known.
    if a is b:
        return True
    if PyMapping_Length(a) != PyMapping_Length(b):
        return False
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cpdef inline bint map_check(object o) noexcept:
    return PyMapping_Check(o)

cpdef inline bint map_eq(object a, object b):
    return mapeq(a, b)

cpdef inline Py_ssize_t map_len(object o) except -1:
    return PyMapping_Length(o)

cpdef inline bint map_has_key(object o, object key) noexcept:
    return PyMapping_HasKey(o, key)

cdef inline bint map_has_key_string(object o, const char *key) noexcept:
    return PyMapping_HasKeyString(o, key)

cpdef inline int map_del(object o, object key) except -1:
    return PyMapping_DelItem(o, key)

cdef inline int map_del_string(object o, const char *key) except -1:
    return PyMapping_DelItemString(o, key)

cpdef inline object map_keys(object o):
    return PyMapping_Keys(o)

cpdef inline object map_values(object o):
    return PyMapping_Values(o)

cpdef inline object map_items(object o):
    return PyMapping_Items(o)

cdef inline object map_getitem_string(object o, const char *key):
    return PyMapping_GetItemString(o, key)

cdef inline int map_setitem_string(object o, const char *key, object v) except -1:
    return PyMapping_SetItemString(o, key, v)
# N2 preferred *_cstr (0.3: *_string cdef-only where soft)

cpdef inline bint map_has_key_cstr(object o, const char *key) noexcept:
    return map_has_key_string(o, key)

cpdef inline int map_del_cstr(object o, const char *key) except -1:
    return map_del_string(o, key)

cpdef inline object map_getitem_cstr(object o, const char *key):
    return map_getitem_string(o, key)

cpdef inline int map_setitem_cstr(object o, const char *key, object v) except -1:
    return map_setitem_string(o, key, v)
