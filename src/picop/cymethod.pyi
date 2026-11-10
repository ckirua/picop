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
    Matches builtins such as ``len`` and C-method descriptors; ``method_check``
    only matches Python bound methods.
    """
    ...

def cfunction_check_exact(o: object) -> bool:
    """Return True if ``o`` is exactly ``PyCFunction`` (``PyCFunction_CheckExact``)."""
    ...

def cmethod_check(o: object) -> bool:
    """Return True if ``o`` is a C method (``PyCMethod_Check``).

    Notes
    -----
    A ``PyCMethod`` is a C function carrying the defining class — the object you
    get from ``type.__dict__`` lookups of slot-backed methods.
    """
    ...

def cmethod_check_exact(o: object) -> bool:
    """Return True if ``o`` is exactly ``PyCMethod`` (``PyCMethod_CheckExact``)."""
    ...

def cfunction_get_self(func: object) -> object | None:
    """Return the class a C function is bound to, or ``None``.

    Notes
    -----
    ``PyCFunction_GetSelf``. Plain builtins and static methods have no ``self``
    and return ``None``; a non-C-function argument raises ``SystemError``.
    """
    ...

def classmethod_new(callable: object) -> object:
    """Return ``classmethod(callable)`` via ``PyClassMethod_New``."""
    ...

def staticmethod_new(callable: object) -> object:
    """Return ``staticmethod(callable)`` via ``PyStaticMethod_New``."""
    ...
