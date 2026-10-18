"""Context / ContextVar helpers wrapping ``PyContext_*`` / ``PyContextVar_*``.

Prefer :mod:`contextvars` from Python unless you need C-API enter/exit or
var construction. ContextVar names take ``bytes``. See
:doc:`/user_guide/safety`.
"""

def context_eq(a: object, b: object) -> bool:
    """Return True if ``Context`` values match (identity + richcompare; same as ``Context.__eq__``)."""
    ...

def ctx_check_exact(obj: object) -> bool:
    """Return True if ``type(obj) is contextvars.Context``."""
    ...

def ctxvar_check_exact(obj: object) -> bool:
    """Return True if ``type(obj) is contextvars.ContextVar``."""
    ...

def ctxtoken_check_exact(obj: object) -> bool:
    """Return True if ``type(obj) is contextvars.Token``."""
    ...

def ctx_new() -> object:
    """Return a new empty ``Context`` (``PyContext_New``)."""
    ...

def ctx_copy(ctx: object) -> object:
    """Return a copy of ``ctx`` (``PyContext_Copy``)."""
    ...

def ctx_copy_current() -> object:
    """Return a copy of the current context (``PyContext_CopyCurrent``)."""
    ...

def ctx_enter(ctx: object) -> int:
    """Enter context ``ctx`` (``PyContext_Enter``).

    Notes
    -----
    Returns ``0`` on success; errors raise — do not use the status as a bool.
    """
    ...

def ctx_exit(ctx: object) -> int:
    """Exit context ``ctx`` (``PyContext_Exit``).

    Notes
    -----
    Returns ``0`` on success; errors raise — do not use the status as a bool.
    """
    ...

def ctxvar_new(name: bytes, default_value: object = None) -> object:
    """Return a new ``ContextVar`` (``PyContextVar_New``).

    Notes
    -----
    ``name`` must be ``bytes``, not ``str``.
    """
    ...

def ctxvar_set(var: object, value: object) -> object:
    """Set ``var`` to ``value``; return a reset token (``PyContextVar_Set``)."""
    ...

def ctxvar_reset(var: object, token: object) -> int:
    """Reset ``var`` using ``token`` (``PyContextVar_Reset``).

    Notes
    -----
    Returns ``0`` on success; errors raise — do not use the status as a bool.
    """
    ...
