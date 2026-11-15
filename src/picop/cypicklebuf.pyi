"""PickleBuffer C-API helpers, available on every supported CPython (3.14 and 3.15)."""

def pickle_buffer_from_object(obj: object) -> object:
    """Create a PickleBuffer from a buffer-protocol object.

    Notes
    -----
    Mixed Tier A parity: 1.50x (3.14), 2.27x (3.14t), 1.31x (3.15), 1.80x (3.15t);
    the typed Cython call site.

    Tier A shows this is slower than the plain-Python equivalent
    `memoryview(obj)` construction; use when pickle protocol semantics are required.
    """

def pickle_buffer_release(obj: object) -> None:
    """Release the exported buffer held by a PickleBuffer."""

def pickle_buffer_check(obj: object) -> bool:
    """Return whether obj is exactly a PickleBuffer instance."""

def pickle_buffer_type() -> type:
    """Return the PickleBuffer type object."""
