"""Typed C-API helpers for :class:`bytearray` hot paths.

Prefer :mod:`picop.cybytearray` (or starters in :mod:`picop.hot`) over builtin
``bytearray`` methods when the concrete type is known. See
:doc:`/user_guide/quickstart` for import patterns.
"""

# Preferred public names (0.3 hard trim)

def bytearray_check(p: object) -> bool:
    """Return True if ``p`` is a :class:`bytearray` or subtype (``PyByteArray_Check``)."""
    ...

def bytearray_check_exact(p: object) -> bool:
    """Return True if ``type(p) is bytearray`` (``PyByteArray_CheckExact``)."""
    ...

def bytearray_concat(a: object, b: object) -> bytearray:
    """Return a new bytearray concatenating ``a`` and ``b`` via ``PyByteArray_Concat``."""
    ...

def bytearray_from_object(o: object) -> bytearray:
    """Return ``bytearray(o)`` via ``PyByteArray_FromObject`` (buffer protocol)."""
    ...

def bytearray_len(ba: bytearray) -> int:
    """Return ``len(ba)`` via ``PyByteArray_GET_SIZE``."""
    ...

def bytearray_eq(a: bytearray, b: bytearray) -> bool:
    """Return True if typed ``bytearray`` values are equal.

    Notes
    -----
    Identity/len short-circuit plus ``memcmp``.
    """
    ...

def bytearray_ne(a: bytearray, b: bytearray) -> bool:
    """Return True if typed ``bytearray`` values differ (``not bytearray_eq``)."""
    ...

def bytearray_contains(haystack: bytearray, needle: bytes) -> bool:
    """Return True if ``needle`` is found in typed ``haystack``.

    Notes
    -----
    Mirrors ``bytes_contains`` search strategy on a typed ``bytearray``.
    """
    ...

def bytearray_resize(ba: bytearray, n: int) -> int:
    """Resize ``ba`` in place via ``PyByteArray_Resize``.

    Notes
    -----
    Returns ``0`` on success and ``-1`` on error; errors raise. Do not use the
    status int as a bool.
    """
    ...

def bytearray_size(ba: object) -> int:
    """Return ``len(ba)`` via checked ``PyByteArray_Size``.

    Notes
    -----
    Prefer ``bytearray_len`` on a typed ``bytearray`` hot path.
    """
    ...
