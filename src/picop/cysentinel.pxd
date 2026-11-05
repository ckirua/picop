# cysentinel.pxd
# ``sentinel`` helpers (new in CPython 3.15), version-gated through
# ``cysentinel_shim.h`` so the module still builds on 3.14.
# Public docs in ``cysentinel.pyi``.

from cpython.unicode cimport PyUnicode_AsUTF8

cdef extern from "cysentinel_shim.h":
    bint cy_sentinel_check(object obj) noexcept
    bint cy_sentinel_check_exact(object obj) noexcept
    object cy_sentinel_new(const char *name, const char *module, const char *repr)
    object cy_sentinel_type()

cpdef inline object sentinel_type():
    return cy_sentinel_type()



cpdef inline bint sentinel_check(object obj) noexcept:
    return cy_sentinel_check(obj)


cpdef inline bint sentinel_check_exact(object obj) noexcept:
    return cy_sentinel_check_exact(obj)


cpdef inline object sentinel_new(object name, object module=None, object repr=None):
    cdef const char *c_name = NULL
    cdef const char *c_module = NULL
    cdef const char *c_repr = NULL
    if not isinstance(name, str):
        raise TypeError("sentinel_new name must be str")
    if module is not None and not isinstance(module, str):
        raise TypeError("sentinel_new module must be str or None")
    if repr is not None and not isinstance(repr, str):
        raise TypeError("sentinel_new repr must be str or None")
    # Reject embedded NULs: the C API accepts NUL-terminated strings.
    if "\0" in name or (module is not None and "\0" in module) or (repr is not None and "\0" in repr):
        raise ValueError("sentinel_new strings must not contain embedded NUL characters")
    # Borrowed UTF-8 views are used only for this call; optional arguments stay
    # NULL when unset, matching the shim's convention.
    c_name = PyUnicode_AsUTF8(name)
    if module is not None:
        c_module = PyUnicode_AsUTF8(module)
    if repr is not None:
        c_repr = PyUnicode_AsUTF8(repr)
    return cy_sentinel_new(c_name, c_module, c_repr)
