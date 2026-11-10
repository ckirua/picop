"""PickleBuffer C-API helpers, available on CPython 3.15 and newer."""

def pickle_buffer_from_object(obj: object) -> object:
    """Create a PickleBuffer from a buffer-protocol object.

    Notes
    -----
    Tier A shows this is slower than the plain-Python equivalent
    `memoryview(obj)` construction; use when pickle protocol semantics are required.
    """

def pickle_buffer_release(obj: object) -> None:
    """Release the exported buffer held by a PickleBuffer.

    Notes
    -----
    Requires CPython 3.15 or newer.
    """

def pickle_buffer_check(obj: object) -> bool:
    """Return whether obj is exactly a PickleBuffer instance.

    Notes
    -----
    Requires CPython 3.15 or newer.
    """

def pickle_buffer_type() -> type:
    """Return the PickleBuffer type object.

    Notes
    -----
    Requires CPython 3.15 or newer.
    """
