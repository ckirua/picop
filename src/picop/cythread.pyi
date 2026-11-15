"""Thread and interpreter lifecycle helpers."""

def guards_supported() -> bool:
    """Return True when CPython provides interpreter guards (3.15+)."""
    ...

def interpreter_guard() -> object:
    """Context manager preventing interpreter finalization (CPython 3.15+).

    Notes
    -----
    Slower than the plain-Python equivalent ``lambda: None`` (Tier A 3.85x); the
    typed Cython call site.
    """
    ...
