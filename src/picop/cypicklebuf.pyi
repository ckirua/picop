"""PickleBuffer C-API helpers, available on every supported CPython (3.14 and 3.15)."""

def pickle_buffer_from_object(obj: object) -> object:
    """Create a PickleBuffer from a buffer-protocol object.

    Notes
    -----
    Mixed Tier A parity: 0.21x (3.15: pickle.dumps buffer-backed record n=248),
    0.22x (3.14: pickle.dumps buffer-backed record n=248), 1.97x (3.14: bytearray
    n=6), 2.17x (3.15: bytearray n=6), 2.98x (3.14: bytearray n=4096), 3.21x (3.15:
    bytearray n=4096), 3.34x (3.14: bytearray n=248), 3.56x (3.15: bytearray n=248);
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
