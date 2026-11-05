# cyfrozendict.pxd
# ``frozendict`` helpers (new in CPython 3.15), version-gated through
# ``cyfrozendict_shim.h`` so the module still builds on 3.14.
# Public docs in ``cyfrozendict.pyi``.

cdef extern from "cyfrozendict_shim.h":
    bint cy_frozendict_check(object obj) noexcept
    bint cy_frozendict_check_exact(object obj) noexcept
    bint cy_anydict_check(object obj) noexcept
    bint cy_anydict_check_exact(object obj) noexcept
    object cy_frozendict_new(object iterable)
    object cy_frozendict_new_empty()
    Py_ssize_t cy_anydict_len(object obj) noexcept


cpdef inline bint frozendict_check(object obj) noexcept:
    return cy_frozendict_check(obj)


cpdef inline bint frozendict_check_exact(object obj) noexcept:
    return cy_frozendict_check_exact(obj)


cpdef inline bint anydict_check(object obj) noexcept:
    return cy_anydict_check(obj)


cpdef inline bint anydict_check_exact(object obj) noexcept:
    return cy_anydict_check_exact(obj)


# ``frozendict_new`` / ``frozendict_empty`` are alloc-heavy but stay in the
# header so cimporters (including the barrel) see the whole surface.


cpdef inline object frozendict_new(object iterable):
    return cy_frozendict_new(iterable)


cpdef inline object frozendict_empty():
    return cy_frozendict_new_empty()


cpdef inline Py_ssize_t anydict_len(object obj) except -1:
    if not cy_anydict_check(obj):
        raise TypeError("anydict_len expects a dict or frozendict")
    return cy_anydict_len(obj)
