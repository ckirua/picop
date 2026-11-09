"""Type-object checks and identity equality via ``PyType_*``.

Prefer builtins for ordinary ``isinstance`` / ``type`` work from Python. Tier A
losers remain ``cpdef`` and carry a parity note in the stub. See
:doc:`/user_guide/quickstart`.
"""

def type_check(o: object) -> bool:
    """Return True if ``o`` is a type object or subtype (``PyType_Check``)."""
    ...

def type_check_exact(o: object) -> bool:
    """Return True if ``type(o) is type`` (``PyType_CheckExact``)."""
    ...

def type_eq(a: object, b: object) -> bool:
    """Return True if ``a is b`` (type-object identity; not metaclass ``__eq__``)."""
    ...

def type_is_subtype(a: object, b: object) -> bool:
    """Return True if ``a`` is a subtype of ``b`` (``PyType_IsSubtype``).

    Notes
    -----
    Slower than the plain-Python equivalent ``issubclass(a, b)`` (Tier A
    1.07–1.09x); the typed Cython call site.
    """
    ...
