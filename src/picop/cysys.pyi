"""CPython sysmodule.h attribute access helpers."""

def sys_get_attr(name: object) -> object:
    """Return a sys attribute by name; raise RuntimeError when it is absent.

    Requires CPython 3.15 or newer.
    """
