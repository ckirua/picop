# cydict.pxd
# Typed ``dict`` helpers. Public docs live in ``cydict.pyi``.
# C-string key APIs and borrowed Next pointers: cdef.

from cpython.object cimport PyObject, PyObject_RichCompareBool, Py_EQ


cdef extern from "Python.h":
    void Py_DECREF(PyObject *o)
    bint PyDict_Check(object p) noexcept
    bint PyDict_CheckExact(object p) noexcept
    dict PyDict_New()
    object PyDictProxy_New(object mapping)
    void PyDict_Clear(object mp) noexcept
    bint PyDict_Contains(object mp, object key) except -1
    int PyDict_ContainsString(object mp, const char *key) except -1
    dict PyDict_Copy(object mp)
    int PyDict_SetItem(object mp, object key, object val) except -1
    int PyDict_SetItemString(object mp, const char *key, object val) except -1
    int PyDict_DelItem(object mp, object key) except -1
    int PyDict_DelItemString(object mp, const char *key) except -1
    PyObject* PyDict_GetItem(object mp, object key) noexcept
    PyObject* PyDict_GetItemWithError(object mp, object key) except? NULL
    PyObject* PyDict_GetItemString(object mp, const char *key) noexcept
    int PyDict_GetItemRef(object mp, object key, PyObject **result) except -1
    int PyDict_GetItemStringRef(object mp, const char *key, PyObject **result) except -1
    PyObject* PyDict_SetDefault(object mp, object key, object default_value) except? NULL
    int PyDict_SetDefaultRef(object mp, object key, object default_value, PyObject **result) except -1
    list PyDict_Items(object mp)
    list PyDict_Keys(object mp)
    list PyDict_Values(object mp)
    Py_ssize_t PyDict_Size(object mp) except -1
    Py_ssize_t PyDict_GET_SIZE(object mp) noexcept
    bint PyDict_Next(object mp, Py_ssize_t *pos, PyObject **key, PyObject **val) noexcept
    int PyDict_Merge(object mp, object other, int override) except -1
    int PyDict_Update(object mp, object other) except -1
    int PyDict_MergeFromSeq2(object mp, object seq2, int override) except -1
    # 3.13+: status pop — 1 found, 0 missing, -1 error
    int PyDict_Pop(object mp, object key, PyObject **result) except -1
    int PyDict_PopString(object mp, const char *key, PyObject **result) except -1


cdef inline bint dcheck(object p) noexcept:
    return PyDict_Check(p)


cdef inline bint dcheck_exact(object p) noexcept:
    return PyDict_CheckExact(p)


cdef inline dict dnew():
    return PyDict_New()


cdef inline object dproxy(dict d):
    # Read-only mappingproxy over ``d``.
    return PyDictProxy_New(d)


cdef inline object dget(dict d, str key) noexcept:
    # Borrowed GetItem; missing and stored None both look like None.
    cdef PyObject *res = PyDict_GetItem(d, key)
    if res is NULL:
        return None
    return <object>res


cdef inline object dget_with_error(dict d, object key):
    # Like GetItem but hash/eq errors propagate (except? NULL).
    cdef PyObject *res = PyDict_GetItemWithError(d, key)
    if res is NULL:
        return None
    return <object>res


cdef inline object dget_ref(dict d, object key):
    # Strong-ref get; distinguishes missing (None) from stored None.
    cdef PyObject *res = NULL
    cdef int rc = PyDict_GetItemRef(d, key, &res)
    cdef object out
    if rc <= 0:
        return None
    out = <object>res
    Py_DECREF(res)
    return out


cdef inline bint dcontains(dict d, str key) except -1:
    return PyDict_Contains(d, key)


cdef inline Py_ssize_t dlen(dict d) noexcept:
    return PyDict_GET_SIZE(d)


cdef inline bint deq(dict a, dict b):
    # Identity / size short-circuit + richcompare (same semantics as ``==``).
    if a is b:
        return True
    if PyDict_GET_SIZE(a) != PyDict_GET_SIZE(b):
        return False
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cdef inline Py_ssize_t dsize(object d) except -1:
    return PyDict_Size(d)


cdef inline int dset(dict d, str key, object value) except -1:
    return PyDict_SetItem(d, key, value)


cdef inline int ddel(dict d, str key) except -1:
    return PyDict_DelItem(d, key)


cdef inline object dpop(dict d, str key):
    # ``d.pop(key, None)`` via PyDict_Pop; None if missing.
    cdef PyObject *res = NULL
    cdef int rc = PyDict_Pop(d, key, &res)
    cdef object out
    if rc <= 0:
        return None
    out = <object>res
    Py_DECREF(res)
    return out


cdef inline int dupdate(dict d, dict other) except -1:
    # Alias of Merge(..., override=1).
    return PyDict_Update(d, other)


cdef inline int dmerge(dict d, object other, bint override=True) except -1:
    return PyDict_Merge(d, other, 1 if override else 0)


cdef inline int dmerge_from_seq2(dict d, object seq2, bint override=True) except -1:
    return PyDict_MergeFromSeq2(d, seq2, 1 if override else 0)


cdef inline object dsetdefault(dict d, str key, object default=None):
    # Borrowed SetDefault — cast INCREFs for Python return.
    cdef PyObject *res = PyDict_SetDefault(d, key, default)
    if res is NULL:
        return None
    return <object>res


cdef inline object dsetdefault_ref(dict d, object key, object default=None):
    # Strong-ref SetDefaultRef; returns existing or inserted value.
    cdef PyObject *res = NULL
    cdef int rc = PyDict_SetDefaultRef(d, key, default, &res)
    cdef object out
    if rc < 0 or res is NULL:
        return None
    out = <object>res
    Py_DECREF(res)
    return out


cdef inline void dclear(dict d) noexcept:
    PyDict_Clear(d)


cdef inline dict dcopy(dict d):
    return PyDict_Copy(d)


cdef inline list dkeys(dict d):
    return PyDict_Keys(d)


cdef inline list dvalues(dict d):
    return PyDict_Values(d)


cdef inline list ditems(dict d):
    return PyDict_Items(d)


cdef inline bint dnext(dict d, Py_ssize_t *pos, PyObject **key, PyObject **val) noexcept:
    # Borrowed key/value pointers — do not DECREF.
    return PyDict_Next(d, pos, key, val)


cdef inline int dset_string(dict d, const char *key, object value) except -1:
    return PyDict_SetItemString(d, key, value)


cdef inline int ddel_string(dict d, const char *key) except -1:
    return PyDict_DelItemString(d, key)


cdef inline object dget_string(dict d, const char *key) noexcept:
    # Borrowed GetItemString; builds a temporary unicode key internally.
    cdef PyObject *res = PyDict_GetItemString(d, key)
    if res is NULL:
        return None
    return <object>res


cdef inline object dget_string_ref(dict d, const char *key):
    cdef PyObject *res = NULL
    cdef int rc = PyDict_GetItemStringRef(d, key, &res)
    cdef object out
    if rc <= 0:
        return None
    out = <object>res
    Py_DECREF(res)
    return out


cdef inline bint dcontains_string(dict d, const char *key) except -1:
    return PyDict_ContainsString(d, key)


cdef inline object dpop_string(dict d, const char *key):
    cdef PyObject *res = NULL
    cdef int rc = PyDict_PopString(d, key, &res)
    cdef object out
    if rc <= 0:
        return None
    out = <object>res
    Py_DECREF(res)
    return out

# Wave 4 N1/N5 preferred names (0.3: soft letter/bare are cdef-only)

cpdef inline bint dict_check(object p) noexcept:
    return dcheck(p)

cpdef inline bint dict_check_exact(object p) noexcept:
    return dcheck_exact(p)

cpdef inline void dict_clear(dict d) noexcept:
    dclear(d)

cpdef inline bint dict_contains(dict d, str key) except -1:
    return dcontains(d, key)

cdef inline bint dict_contains_string(dict d, const char *key) except -1:
    return dcontains_string(d, key)

cpdef inline dict dict_copy(dict d):
    return dcopy(d)

cpdef inline int dict_del(dict d, str key) except -1:
    return ddel(d, key)

cdef inline int dict_del_string(dict d, const char *key) except -1:
    return ddel_string(d, key)

cpdef inline object dict_get(dict d, str key) noexcept:
    return dget(d, key)

cpdef inline object dict_get_ref(dict d, object key):
    return dget_ref(d, key)

cdef inline object dict_get_string(dict d, const char *key) noexcept:
    return dget_string(d, key)

cdef inline object dict_get_string_ref(dict d, const char *key):
    return dget_string_ref(d, key)

cpdef inline object dict_get_with_error(dict d, object key):
    return dget_with_error(d, key)

cdef inline list dict_items(dict d):
    return ditems(d)

cdef inline list dict_keys(dict d):
    return dkeys(d)

cpdef inline Py_ssize_t dict_len(dict d) noexcept:
    return dlen(d)

cpdef inline bint dict_eq(dict a, dict b):
    return deq(a, b)

cpdef inline int dict_merge(dict d, object other, bint override=True) except -1:
    return dmerge(d, other, override)

cpdef inline int dict_merge_from_seq2(dict d, object seq2, bint override=True) except -1:
    return dmerge_from_seq2(d, seq2, override)

cpdef inline dict dict_new():
    return dnew()

cdef inline bint dict_next(dict d, Py_ssize_t *pos, PyObject **key, PyObject **val) noexcept:
    return dnext(d, pos, key, val)

cpdef inline object dict_pop(dict d, str key):
    return dpop(d, key)

cdef inline object dict_pop_string(dict d, const char *key):
    return dpop_string(d, key)

cpdef inline object dict_proxy(dict d):
    return dproxy(d)

cpdef inline int dict_set(dict d, str key, object value) except -1:
    return dset(d, key, value)

cdef inline int dict_set_string(dict d, const char *key, object value) except -1:
    return dset_string(d, key, value)

cpdef inline object dict_setdefault(dict d, str key, object default=None):
    return dsetdefault(d, key, default)

cpdef inline object dict_setdefault_ref(dict d, object key, object default=None):
    return dsetdefault_ref(d, key, default)

cpdef inline Py_ssize_t dict_size(object d) except -1:
    return dsize(d)

cpdef inline int dict_update(dict d, dict other) except -1:
    return dupdate(d, other)

cdef inline list dict_values(dict d):
    return dvalues(d)

