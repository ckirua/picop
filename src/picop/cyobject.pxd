# cyobject.pxd
# Object protocol helpers. Public docs in ``cyobject.pyi``.
# TypeCheck / TYPE / Malloc family / varargs Call*: cdef.
# Cmp / Compare: ABI-missing on 3.14 — not wrapped.

from cpython.object cimport PyObject, PyTypeObject


cdef extern from "Python.h":
    int Py_LT
    int Py_LE
    int Py_EQ
    int Py_NE
    int Py_GT
    int Py_GE

    bint PyObject_HasAttrString(object o, const char *attr_name) noexcept
    object PyObject_GetAttrString(object o, const char *attr_name)
    bint PyObject_HasAttr(object o, object attr_name) noexcept
    object PyObject_GetAttr(object o, object attr_name)
    object PyObject_GenericGetAttr(object o, object attr_name)
    int PyObject_SetAttrString(object o, const char *attr_name, object v) except -1
    int PyObject_SetAttr(object o, object attr_name, object v) except -1
    int PyObject_GenericSetAttr(object o, object attr_name, object v) except -1
    int PyObject_DelAttrString(object o, const char *attr_name) except -1
    int PyObject_DelAttr(object o, object attr_name) except -1
    object PyObject_RichCompare(object o1, object o2, int opid)
    bint PyObject_RichCompareBool(object o1, object o2, int opid) except -1
    object PyObject_Repr(object o)
    object PyObject_Str(object o)
    object PyObject_Bytes(object o)
    bint PyObject_IsInstance(object inst, object cls) except -1
    bint PyObject_IsSubclass(object derived, object cls) except -1
    bint PyCallable_Check(object o) noexcept
    object PyObject_Call(object callable_object, object args, object kw)
    object PyObject_CallObject(object callable_object, object args)
    long PyObject_Hash(object o) except? -1
    bint PyObject_IsTrue(object o) except -1
    bint PyObject_Not(object o) except -1
    object PyObject_Type(object o)
    bint PyObject_TypeCheck(object o, PyTypeObject *type) noexcept
    Py_ssize_t PyObject_Length(object o) except -1
    Py_ssize_t PyObject_Size(object o) except -1
    Py_ssize_t PyObject_LengthHint(object o, Py_ssize_t default_value) except -1
    object PyObject_GetItem(object o, object key)
    int PyObject_SetItem(object o, object key, object v) except -1
    int PyObject_DelItem(object o, object key) except -1
    int PyObject_AsFileDescriptor(object o) except -1
    object PyObject_Dir(object o)
    object PyObject_GetIter(object o)
    object PyObject_Format(object obj, object format_spec)
    PyTypeObject *Py_TYPE(object o) noexcept
    void *PyObject_Malloc(size_t size) noexcept
    void *PyObject_Realloc(void *ptr, size_t size) noexcept
    void PyObject_Free(void *ptr) noexcept


cpdef inline bint obj_hasattr(object o, object name) noexcept:
    return PyObject_HasAttr(o, name)


cdef inline bint obj_hasattr_string(object o, const char *name) noexcept:
    return PyObject_HasAttrString(o, name)


cpdef inline object obj_getattr(object o, object name):
    return PyObject_GetAttr(o, name)


cdef inline object obj_getattr_string(object o, const char *name):
    return PyObject_GetAttrString(o, name)


cpdef inline int obj_setattr(object o, object name, object v) except -1:
    return PyObject_SetAttr(o, name, v)


cdef inline int obj_setattr_string(object o, const char *name, object v) except -1:
    return PyObject_SetAttrString(o, name, v)


cpdef inline int obj_delattr(object o, object name) except -1:
    return PyObject_DelAttr(o, name)


cdef inline int obj_delattr_string(object o, const char *name) except -1:
    return PyObject_DelAttrString(o, name)


cpdef inline object obj_richcompare(object o1, object o2, int opid):
    return PyObject_RichCompare(o1, o2, opid)


cpdef inline bint obj_richcompare_bool(object o1, object o2, int opid) except -1:
    return PyObject_RichCompareBool(o1, o2, opid)


cdef inline bint oeq(object a, object b) except -1:
    # Generic object equality via ``PyObject_RichCompareBool`` (``Py_EQ``).
    # Identity short-circuit (incl. ``nan is nan`` → True) — same as the C-API,
    # not always Python ``==`` for floats. Prefer typed ``*_eq`` when known.
    # Soft ``oeq``. Not on ``hot`` — validate win before promoting.
    return PyObject_RichCompareBool(a, b, Py_EQ)


cpdef inline bint obj_eq(object a, object b) except -1:
    return oeq(a, b)


cpdef inline object obj_repr(object o):
    return PyObject_Repr(o)


cpdef inline object obj_str(object o):
    return PyObject_Str(o)


cpdef inline object obj_bytes(object o):
    return PyObject_Bytes(o)


cpdef inline bint obj_isinstance(object inst, object cls) except -1:
    return PyObject_IsInstance(inst, cls)


cpdef inline bint obj_issubclass(object derived, object cls) except -1:
    return PyObject_IsSubclass(derived, cls)


cpdef inline bint obj_callable(object o) noexcept:
    return PyCallable_Check(o)


cpdef inline object obj_call(object callable_object, object args, object kw=None):
    return PyObject_Call(callable_object, args, kw)


cpdef inline object obj_call_object(object callable_object, object args):
    return PyObject_CallObject(callable_object, args)


cpdef inline long obj_hash(object o) except? -1:
    return PyObject_Hash(o)


cpdef inline bint obj_istrue(object o) except -1:
    return PyObject_IsTrue(o)


cpdef inline bint obj_not(object o) except -1:
    return PyObject_Not(o)


cpdef inline object obj_type(object o):
    return PyObject_Type(o)


cpdef inline Py_ssize_t obj_len(object o) except -1:
    return PyObject_Length(o)


cpdef inline Py_ssize_t obj_size(object o) except -1:
    # Alias of Length (cheap sibling).
    return PyObject_Size(o)


cpdef inline Py_ssize_t obj_length_hint(object o, Py_ssize_t default_value) except -1:
    return PyObject_LengthHint(o, default_value)


cpdef inline object obj_getitem(object o, object key):
    return PyObject_GetItem(o, key)


cpdef inline int obj_setitem(object o, object key, object v) except -1:
    return PyObject_SetItem(o, key, v)


cpdef inline int obj_delitem(object o, object key) except -1:
    return PyObject_DelItem(o, key)


cpdef inline int obj_as_fd(object o) except -1:
    return PyObject_AsFileDescriptor(o)


cpdef inline object obj_dir(object o):
    return PyObject_Dir(o)


cpdef inline object obj_iter(object o):
    return PyObject_GetIter(o)


cpdef inline object obj_format(object obj, object format_spec):
    return PyObject_Format(obj, format_spec)


cdef inline bint obj_typecheck(object o, PyTypeObject *type) noexcept:
    return PyObject_TypeCheck(o, type)


cdef inline PyTypeObject *obj_type_ptr(object o) noexcept:
    return Py_TYPE(o)


cdef inline object obj_generic_getattr(object o, object name):
    return PyObject_GenericGetAttr(o, name)


cdef inline int obj_generic_setattr(object o, object name, object v) except -1:
    return PyObject_GenericSetAttr(o, name, v)


cdef inline void *obj_malloc(size_t size) noexcept:
    return PyObject_Malloc(size)


cdef inline void *obj_realloc(void *ptr, size_t size) noexcept:
    return PyObject_Realloc(ptr, size)


cdef inline void obj_free(void *ptr) noexcept:
    PyObject_Free(ptr)
# N2 preferred *_cstr (0.3: *_string cdef-only where soft)

cpdef inline bint obj_hasattr_cstr(object o, const char *name) noexcept:
    return obj_hasattr_string(o, name)

cpdef inline object obj_getattr_cstr(object o, const char *name):
    return obj_getattr_string(o, name)

cpdef inline int obj_setattr_cstr(object o, const char *name, object v) except -1:
    return obj_setattr_string(o, name, v)

cpdef inline int obj_delattr_cstr(object o, const char *name) except -1:
    return obj_delattr_string(o, name)
