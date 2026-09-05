"""Python function-object accessors wrapping ``PyFunction_*``.

Prefer attribute access from Python unless you need owned-ref C-API getters
on a known function object. Status-int setters return ``0`` on success. See
:doc:`/user_guide/quickstart`.
"""

def func_check(o: object) -> bool:
    """Return True if ``o`` is a Python function object (``PyFunction_Check``)."""
    ...

def func_eq(a: object, b: object) -> bool:
    """Return True if ``a is b`` (function-object identity; CPython ``object.__eq__``)."""
    ...

def func_new(code: object, globals: object) -> object:
    """Return a new function from ``code`` and ``globals`` (``PyFunction_New``)."""
    ...

def func_get_code(op: object) -> object:
    """Return the code object of function ``op`` (owned ref)."""
    ...

def func_get_globals(op: object) -> object:
    """Return the globals dict of function ``op`` (owned ref)."""
    ...

def func_get_module(op: object) -> object | None:
    """Return ``op.__module__`` (owned ref), or ``None`` if unset."""
    ...

def func_get_defaults(op: object) -> object | None:
    """Return argument defaults tuple of ``op``, or ``None``."""
    ...

def func_set_defaults(op: object, defaults: object) -> int:
    """Set argument defaults on ``op`` (``None`` or tuple).

    Notes
    -----
    Returns ``0`` on success; errors raise — do not use the status as a bool.
    """
    ...

def func_get_closure(op: object) -> object | None:
    """Return closure cell tuple of ``op``, or ``None``."""
    ...

def func_set_closure(op: object, closure: object) -> int:
    """Set closure on ``op`` (``None`` or cell tuple).

    Notes
    -----
    Returns ``0`` on success; errors raise — do not use the status as a bool.
    """
    ...
