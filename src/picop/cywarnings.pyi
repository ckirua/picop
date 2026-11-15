"""Public warning helpers."""

def warn_ex(category: type[Warning], message: object, stacklevel: int = 1) -> bool:
    """Issue a warning through CPython's active filters.

    Return ``False`` when handled; let filter-selected exceptions propagate.

    Notes
    -----
    Mixed Tier A parity: 0.86x (3.14: vs warnings.warn stacklevel=2), 0.92x (3.15:
    vs warnings.warn stacklevel=2), 1.02x (3.14: vs warnings.warn), 1.10x (3.15: vs
    warnings.warn); the typed Cython call site.
    """

def warn_explicit(category: type[Warning], message: object, filename: str, lineno: int, module: str | None = None, registry: dict | None = None) -> bool:
    """Issue a warning at an explicit source location through CPython's filters.

    Return ``False`` when handled; let filter-selected exceptions propagate.
    """

def warnings_module() -> object | None:
    """Return the initialized warnings module, or None if unavailable."""
