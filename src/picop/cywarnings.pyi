"""Public warning helpers."""

def warn_ex(category: type[Warning], message: object, stacklevel: int = 1) -> bool:
    """Issue a warning through CPython's active filters.

    Return ``False`` when handled; let filter-selected exceptions propagate.
    """

def warn_explicit(category: type[Warning], message: object, filename: str, lineno: int, module: str | None = None, registry: dict | None = None) -> bool:
    """Issue a warning at an explicit source location through CPython's filters.

    Return ``False`` when handled; let filter-selected exceptions propagate.
    """

def warnings_module() -> object | None:
    """Return the initialized warnings module, or None if unavailable."""
