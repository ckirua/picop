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
    Mixed Tier A parity: 0.95x (3.15: int!<bool), 0.95x (3.15: bool<int), 1.02x
    (3.14: bool<int), 1.04x (3.14: int!<bool); the typed Cython call site.
    """
    ...
