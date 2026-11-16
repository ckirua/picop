"""PickleBuffer C-API helpers, available on every supported CPython (3.14 and 3.15)."""

def pickle_buffer_from_object(obj: object) -> object:
    """Create a PickleBuffer from a buffer-protocol object.

    Notes
    -----
    Mixed Tier A parity: 1.96x (bytearray n=248), 1.14x (bytearray n=4096), 1.51x
    (bytearray n=6), 0.10x (pickle.dumps buffer-backed record n=248); the typed
    Cython call site.

    Tier A shows this is slower than the plain-Python equivalent
    `memoryview(obj)` construction; use when pickle protocol semantics are required.
    """

def pickle_buffer_release(obj: object) -> None:
    """Release the exported buffer held by a PickleBuffer."""

def pickle_buffer_check(obj: object) -> bool:
    """Return whether obj is exactly a PickleBuffer instance."""

def pickle_buffer_type() -> type:
    """Return the PickleBuffer type object."""
