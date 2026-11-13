"""CPython sysmodule.h attribute access helpers."""

def sys_get_attr(name: object) -> object:
    """Return a sys attribute by name; raise RuntimeError when it is absent.

    Requires CPython 3.15 or newer.
    """

def lazy_imports_supported() -> bool:
    """Return True when the interpreter provides lazy-import controls (CPython 3.15+)."""

def lazy_import_mode() -> str:
    """Return the lazy-import mode, "normal" or "all". Requires CPython 3.15+."""

def set_lazy_import_mode(mode: str) -> None:
    """Set the lazy-import mode to "normal" or "all". Requires CPython 3.15+."""
