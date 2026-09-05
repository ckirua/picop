# cypycapsule.pxd
# Capsule helpers. CheckExact public; pointer APIs cimport-only.

cdef extern from "Python.h":
    bint PyCapsule_CheckExact(object o) noexcept
    object PyCapsule_New(void *pointer, const char *name, void *destructor)
    void *PyCapsule_GetPointer(object capsule, const char *name) except? NULL
    bint PyCapsule_IsValid(object capsule, const char *name) noexcept
    const char *PyCapsule_GetName(object capsule) except? NULL
    void *PyCapsule_GetContext(object capsule) except? NULL
    int PyCapsule_SetPointer(object capsule, void *pointer) except -1
    int PyCapsule_SetName(object capsule, const char *name) except -1
    int PyCapsule_SetContext(object capsule, void *context) except -1
    void *PyCapsule_Import(const char *name, int no_block) except? NULL


cpdef inline bint capsule_check_exact(object o) noexcept:
    return PyCapsule_CheckExact(o)


cpdef inline bint capsule_is_valid(object capsule, const char *name) noexcept:
    return PyCapsule_IsValid(capsule, name)


cdef inline bint capsuleeq(object a, object b) noexcept:
    # Capsule equality is identity (CPython uses ``object.__eq__`` —
    # same pointer/name does not make distinct capsules equal). Soft
    # ``capsuleeq``. Callers should pass capsule objects. Not on ``hot``.
    return a is b


cpdef inline bint capsule_eq(object a, object b) noexcept:
    return capsuleeq(a, b)


cdef inline object capsule_new(void *pointer, const char *name, void *destructor=NULL):
    return PyCapsule_New(pointer, name, destructor)


cdef inline void *capsule_get_pointer(object capsule, const char *name) except? NULL:
    return PyCapsule_GetPointer(capsule, name)


cdef inline const char *capsule_get_name(object capsule) except? NULL:
    return PyCapsule_GetName(capsule)


cdef inline void *capsule_get_context(object capsule) except? NULL:
    return PyCapsule_GetContext(capsule)


cdef inline int capsule_set_pointer(object capsule, void *pointer) except -1:
    return PyCapsule_SetPointer(capsule, pointer)


cdef inline int capsule_set_name(object capsule, const char *name) except -1:
    return PyCapsule_SetName(capsule, name)


cdef inline int capsule_set_context(object capsule, void *context) except -1:
    return PyCapsule_SetContext(capsule, context)


cdef inline void *capsule_import(const char *name, int no_block=0) except? NULL:
    return PyCapsule_Import(name, no_block)
