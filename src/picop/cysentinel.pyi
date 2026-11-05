"""Typed checks and constructors for :class:`sentinel` (CPython 3.15+)."""

def sentinel_check(obj: object) -> bool:
    """Return True if ``obj`` is a sentinel.

    Notes
    -----
    The sentinel type cannot be subclassed, so ``sentinel_check`` and
    ``sentinel_check_exact`` agree on every value.
    """
    ...

def sentinel_check_exact(obj: object) -> bool:
    """Return True if ``obj`` is exactly a sentinel (subtypes excluded)."""
    ...

def sentinel_new(name: str, module: str | None = None, repr: str | None = None) -> object:
    """Return a newly created sentinel named ``name``.

    Notes
    -----
    Unlike the builtin ``sentinel`` constructor, ``module`` and ``repr``
    default to ``None`` rather than being inferred. Embedded NUL characters
    raise ``ValueError`` (the C API is NUL-terminated) and unpaired surrogates
    raise ``UnicodeEncodeError``. Raises ``NotImplementedError`` on 3.14.
    """
    ...

def sentinel_type() -> object:
    """Return the builtin ``sentinel`` type.

    Notes
    -----
    Raises ``NotImplementedError`` on CPython 3.14. Prefer the check helpers
    over comparing against this type.
    """
    ...
