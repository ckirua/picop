"""Bound-method checks and accessors wrapping ``PyMethod_*``.

Prefer attribute access from Python unless you need checked C-API getters on a
known method. Tier A losers remain ``cpdef`` and carry a parity note in the
stub. See :doc:`/user_guide/quickstart`.
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

def method_new(func: object, self: object) -> object:
    """Return a bound method for ``func`` and ``self`` (``PyMethod_New``)."""
    ...

def cfunction_check(o: object) -> bool:
    """Return True if ``o`` is a C function object (``PyCFunction_Check``).

    Notes
    -----
    Matches builtin functions and bound C methods such as ``[].append``;
    unbound descriptors such as ``str.join`` are not ``PyCFunction`` objects. A
    ``PyCMethod`` passes here but not in ``cfunction_check_exact``.
    """
    ...

def cfunction_check_exact(o: object) -> bool:
    """Return True if ``o`` is exactly ``PyCFunction`` (``PyCFunction_CheckExact``)."""
    ...

def cmethod_check(o: object) -> bool:
    """Return True if ``o`` is a C method (``PyCMethod_Check``).

    Notes
    -----
    A ``PyCMethod`` is a ``PyCFunction`` carrying the defining class, built by
    ``PyCMethod_New``; unbound descriptors such as ``str.join`` are not
    ``PyCFunction`` objects at all.
    """
    ...

def cmethod_check_exact(o: object) -> bool:
    """Return True if ``o`` is exactly ``PyCMethod`` (``PyCMethod_CheckExact``)."""
    ...

def cfunction_get_self(func: object) -> object | None:
    """Return the object a C function is bound to (its ``__self__``), or ``None``.

    Notes
    -----
    ``PyCFunction_GetSelf`` hands back the borrowed ``m_self``: builtin
    functions report the ``builtins`` module and ``METH_STATIC`` functions
    report ``None``. A non-C-function argument raises ``SystemError``.
    """
    ...

def classmethod_new(callable: object) -> object:
    """Return ``classmethod(callable)`` via ``PyClassMethod_New``."""
    ...

def staticmethod_new(callable: object) -> object:
    """Return ``staticmethod(callable)`` via ``PyStaticMethod_New``."""
    ...
