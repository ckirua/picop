"""Bound-method checks and accessors wrapping ``PyMethod_*``.

Prefer attribute access from Python unless you need checked C-API getters on
a known method. Tier A losers remain ``cpdef`` but are omitted from stubs.
See :doc:`/user_guide/quickstart`.
"""

def method_check(o: object) -> bool:
    """Return True if ``o`` is a bound method (``PyMethod_Check``)."""
    ...

def method_eq(a: object, b: object) -> bool:
    """Return True if methods equal (same function + ``__self__``; not identity)."""
    ...

def method_get_function(meth: object) -> object:
    """Return the underlying function via checked ``PyMethod_Function``.

    Notes
    -----
    Preferred spelling of ``method_function``.
    """
    ...

def method_get_self(meth: object) -> object | None:
    """Return ``__self__`` via checked ``PyMethod_Self``.

    Notes
    -----
    Preferred spelling of ``method_self``.
    """
    ...
