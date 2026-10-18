# cytype.pxd
# Type-object helpers. Public docs in ``cytype.pyi``.
# GenericAlloc/New/Ready/Modified/HasFeature/IS_GC: cdef (type-mutation / flags).
#
# CPython APIs take ``PyTypeObject*``. Declaring them as ``object`` makes Cython
# pass ``PyObject*``, which GCC 14+ rejects as an incompatible-pointer-type error.

cdef extern from "Python.h":
    bint PyType_Check(object o) noexcept
    bint PyType_CheckExact(object o) noexcept
    void PyType_Modified(type typ) noexcept
    bint PyType_HasFeature(type o, unsigned long feature) noexcept
    bint PyType_IS_GC(type o) noexcept
    bint PyType_IsSubtype(type a, type b) noexcept
    object PyType_GenericAlloc(type typ, Py_ssize_t nitems)
    object PyType_GenericNew(type typ, object args, object kwds)
    int PyType_Ready(type typ) except -1


cpdef inline bint type_check(object o) noexcept:
    return PyType_Check(o)


cpdef inline bint type_check_exact(object o) noexcept:
    return PyType_CheckExact(o)


cpdef inline bint type_is_subtype(object a, object b) noexcept:
    return PyType_IsSubtype(<type>a, <type>b)


cdef inline bint typeeq(object a, object b) noexcept:
    # Type-object equality is identity (CPython ``type_richcompare`` default).
    # Not Python ``==`` when a metaclass overrides ``__eq__``. Soft ``typeeq``.
    # Callers should pass type objects. Not on ``hot`` — validate win first.
    return a is b


cpdef inline bint type_eq(object a, object b) noexcept:
    return typeeq(a, b)


cdef inline void type_modified(object typ) noexcept:
    # Invalidate type lookup cache after manual type mutation.
    PyType_Modified(<type>typ)


cdef inline bint type_has_feature(object o, int feature) noexcept:
    return PyType_HasFeature(<type>o, <unsigned long>feature)


cdef inline bint type_is_gc(object o) noexcept:
    return PyType_IS_GC(<type>o)


cdef inline object type_generic_alloc(object typ, Py_ssize_t nitems):
    return PyType_GenericAlloc(<type>typ, nitems)


cdef inline object type_generic_new(object typ, object args, object kwds):
    return PyType_GenericNew(<type>typ, args, kwds)


cdef inline int type_ready(object typ) except -1:
    return PyType_Ready(<type>typ)
