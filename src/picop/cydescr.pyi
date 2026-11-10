"""Descriptor introspection and data-descriptor checks."""

def descr_is_data(descr: object) -> bool:
    """Return True if ``descr`` is a data descriptor."""
    ...

def descr_name(descr: object) -> str:
    """Return the name of a CPython method, member, getset, or wrapper descriptor."""
    ...

def descr_objclass(descr: object) -> type:
    """Return the descriptor's defining type."""
    ...
