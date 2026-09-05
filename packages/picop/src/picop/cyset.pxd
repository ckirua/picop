# cyset.pxd
# Typed ``set`` / any-set helpers. Public docs live in ``cyset.pyi``.
# ``supdate`` uses exported ``_PySet_Update`` (no public PySet_Update).

from cpython.object cimport PyObject, PyObject_RichCompareBool, Py_EQ


cdef extern from "Python.h":
    bint PyAnySet_Check(object p) noexcept
    bint PyAnySet_CheckExact(object p) noexcept
    bint PyFrozenSet_Check(object p) noexcept
    bint PyFrozenSet_CheckExact(object p) noexcept
    bint PySet_Check(object p) noexcept
    bint PySet_CheckExact(object p) noexcept
    object PySet_New(PyObject *iterable)
    object PyFrozenSet_New(PyObject *iterable)
    Py_ssize_t PySet_Size(object anyset) except -1
    Py_ssize_t PySet_GET_SIZE(object anyset) noexcept
    bint PySet_Contains(object anyset, object key) except -1
    int PySet_Add(object set, object key) except -1
    int PySet_Discard(object set, object key) except -1
    object PySet_Pop(object set)
    int PySet_Clear(object set) except -1

# Exported from libpython but not declared in public Python.h (3.14+).
# Provide our own prototype so GCC does not treat the call as an implicit decl.
cdef extern from *:
    """
    #ifndef Cypy_PySet_Update_H
    #define Cypy_PySet_Update_H
    PyAPI_FUNC(int) _PySet_Update(PyObject *set, PyObject *iterable);
    #endif
    """
    int _PySet_Update(object s, object iterable) except -1


cdef inline bint scheck(object p) noexcept:
    return PySet_Check(p)


cdef inline bint scheck_exact(object p) noexcept:
    return PySet_CheckExact(p)


cdef inline bint sany_check(object p) noexcept:
    return PyAnySet_Check(p)


cdef inline bint sany_check_exact(object p) noexcept:
    return PyAnySet_CheckExact(p)


cdef inline bint sfrozen_check(object p) noexcept:
    return PyFrozenSet_Check(p)


cdef inline bint sfrozen_check_exact(object p) noexcept:
    return PyFrozenSet_CheckExact(p)


cdef inline set sempty():
    return <set>PySet_New(NULL)


cdef inline set snew(object iterable):
    return <set>PySet_New(<PyObject *>iterable)


cdef inline frozenset sfrozen_empty():
    return <frozenset>PyFrozenSet_New(NULL)


cdef inline frozenset sfrozen_new(object iterable):
    return <frozenset>PyFrozenSet_New(<PyObject *>iterable)


cdef inline Py_ssize_t slen(set s) noexcept:
    return PySet_GET_SIZE(s)


cdef inline bint seteq(set a, set b):
    # Identity / size short-circuit + richcompare (same semantics as ``==``).
    # Soft name ``seteq`` (not ``seq``) avoids confusion with ``seq_*`` / ``sq*``.
    if a is b:
        return True
    if PySet_GET_SIZE(a) != PySet_GET_SIZE(b):
        return False
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cdef inline bint fseteq(frozenset a, frozenset b):
    # Identity / size short-circuit + richcompare (same semantics as ``==``).
    # Soft name ``fseteq`` mirrors ``seteq`` for frozenset.
    if a is b:
        return True
    if PySet_GET_SIZE(a) != PySet_GET_SIZE(b):
        return False
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cdef inline Py_ssize_t ssize(object anyset) except -1:
    return PySet_Size(anyset)


cdef inline bint scontains(object anyset, object value) except -1:
    return PySet_Contains(anyset, value)


cdef inline int sadd(set s, object value) except -1:
    return PySet_Add(s, value)


cdef inline int sdiscard(set s, object value) except -1:
    # 1 removed, 0 absent (no KeyError), -1 error.
    return PySet_Discard(s, value)


cdef inline object spop(set s):
    # Raises KeyError if empty (unlike prior noexcept→None swallow).
    return PySet_Pop(s)


cdef inline int sclear(set s) except -1:
    return PySet_Clear(s)


cdef inline set scopy(set s):
    return <set>PySet_New(<PyObject *>s)


cdef inline int supdate(set s, object iterable) except -1:
    return _PySet_Update(s, iterable)

# Wave 4 N1/N5 preferred names (0.3: soft letter/bare are cdef-only)

cpdef inline int set_add(set s, object value) except -1:
    return sadd(s, value)

cpdef inline bint set_any_check(object p) noexcept:
    return sany_check(p)

cpdef inline bint set_any_check_exact(object p) noexcept:
    return sany_check_exact(p)

cpdef inline bint set_check(object p) noexcept:
    return scheck(p)

cpdef inline bint set_check_exact(object p) noexcept:
    return scheck_exact(p)

cpdef inline int set_clear(set s) except -1:
    return sclear(s)

cpdef inline bint set_contains(object anyset, object value) except -1:
    return scontains(anyset, value)

cpdef inline set set_copy(set s):
    return scopy(s)

cpdef inline int set_discard(set s, object value) except -1:
    return sdiscard(s, value)

cpdef inline set set_empty():
    return sempty()

cpdef inline bint frozenset_check(object p) noexcept:
    return sfrozen_check(p)

cpdef inline bint frozenset_check_exact(object p) noexcept:
    return sfrozen_check_exact(p)

cpdef inline frozenset frozenset_empty():
    return sfrozen_empty()

cpdef inline frozenset frozenset_new(object iterable):
    return sfrozen_new(iterable)

cpdef inline bint frozenset_eq(frozenset a, frozenset b):
    return fseteq(a, b)

cpdef inline Py_ssize_t set_len(set s) noexcept:
    return slen(s)

cpdef inline bint set_eq(set a, set b):
    return seteq(a, b)

cpdef inline set set_new(object iterable):
    return snew(iterable)

cpdef inline object set_pop(set s):
    return spop(s)

cpdef inline Py_ssize_t set_size(object anyset) except -1:
    return ssize(anyset)

cpdef inline int set_update(set s, object iterable) except -1:
    return supdate(s, iterable)

