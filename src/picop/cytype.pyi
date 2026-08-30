"""Type-object checks and identity equality via ``PyType_*``.

Prefer builtins for ordinary ``isinstance`` / ``type`` work from Python.
Tier A losers remain ``cpdef`` but are omitted from stubs. See
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
