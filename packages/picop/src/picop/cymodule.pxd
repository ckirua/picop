# cymodule.pxd
# Module / import helpers. Public docs in ``cymodule.pyi``.
# GetDict / GetState / AddObject (steals) / ExtendInittab: cdef.
# Prefer ``mod_add_object_ref`` over stealing ``mod_add_object``.

from cpython.object cimport PyObject
from cpython.ref cimport Py_INCREF


cdef extern from "Python.h":
    bint PyModule_Check(object p) noexcept
    bint PyModule_CheckExact(object p) noexcept
    object PyModule_NewObject(object name)
    object PyModule_New(const char *name)
    PyObject *PyModule_GetDict(object module) except? NULL
    object PyModule_GetNameObject(object module)
    char *PyModule_GetName(object module) except? NULL
    void *PyModule_GetState(object module) noexcept
    object PyModule_GetFilenameObject(object module)
    char *PyModule_GetFilename(object module) except? NULL
    int PyModule_AddObject(object module, const char *name, object value) except -1
    int PyModule_AddObjectRef(object module, const char *name, object value) except -1
    int PyModule_AddIntConstant(object module, const char *name, long value) except -1
    int PyModule_AddStringConstant(object module, const char *name, const char *value) except -1
    object PyImport_ImportModule(const char *name)
    object PyImport_Import(object name)
    object PyImport_ReloadModule(object m)
    long PyImport_GetMagicNumber() noexcept
    PyObject *PyImport_GetModuleDict() except? NULL
    PyObject *PyImport_AddModule(const char *name) except? NULL


cpdef inline bint mod_check(object p) noexcept:
    return PyModule_Check(p)


cpdef inline bint mod_check_exact(object p) noexcept:
    return PyModule_CheckExact(p)


cdef inline bint modeq(object a, object b) noexcept:
    # Module equality is identity (CPython uses ``object.__eq__``). Soft
    # ``modeq``. Callers should pass module objects. Not on ``hot``.
    return a is b


cpdef inline bint mod_eq(object a, object b) noexcept:
    return modeq(a, b)


cpdef inline object mod_new(const char *name):
    return PyModule_New(name)


cpdef inline object mod_new_object(object name):
    return PyModule_NewObject(name)


cpdef inline object mod_get_name(object module):
    return PyModule_GetNameObject(module)


cpdef inline object mod_get_filename(object module):
    return PyModule_GetFilenameObject(module)


cpdef inline int mod_add_object_ref(object module, const char *name, object value) except -1:
    return PyModule_AddObjectRef(module, name, value)


cpdef inline int mod_add_int(object module, const char *name, long value) except -1:
    return PyModule_AddIntConstant(module, name, value)


cdef inline int mod_add_string(object module, const char *name, const char *value) except -1:
    return PyModule_AddStringConstant(module, name, value)


cpdef inline object mod_import(const char *name):
    return PyImport_ImportModule(name)


cpdef inline object mod_import_object(object name):
    return PyImport_Import(name)


cpdef inline object mod_reload(object m):
    return PyImport_ReloadModule(m)


cpdef inline long mod_magic_number() noexcept:
    return PyImport_GetMagicNumber()


cdef inline object mod_get_dict(object module):
    cdef PyObject *p = PyModule_GetDict(module)
    if p is NULL:
        return None
    cdef object obj = <object>p
    Py_INCREF(obj)
    return obj


cdef inline int mod_add_object(object module, const char *name, object value) except -1:
    # Steals a reference to value on success.
    return PyModule_AddObject(module, name, value)


cdef inline void *mod_get_state(object module) noexcept:
    return PyModule_GetState(module)


cdef inline object mod_add_module(const char *name):
    cdef PyObject *p = PyImport_AddModule(name)
    if p is NULL:
        return None
    cdef object obj = <object>p
    Py_INCREF(obj)
    return obj


cdef inline object mod_modules_dict():
    cdef PyObject *p = PyImport_GetModuleDict()
    if p is NULL:
        return None
    cdef object obj = <object>p
    Py_INCREF(obj)
    return obj
# N2 preferred *_cstr (0.3: *_string cdef-only where soft)

cpdef inline int mod_add_cstr(object module, const char *name, const char *value) except -1:
    return mod_add_string(module, name, value)
