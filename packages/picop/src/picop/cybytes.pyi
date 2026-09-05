"""Typed C-API helpers for :class:`bytes` hot paths.

Prefer :mod:`picop.cybytes` (or starters in :mod:`picop.hot`) over builtin
``bytes`` methods when the concrete type is known. See
:doc:`/user_guide/quickstart` for import patterns.
"""

# Preferred public names (0.3 hard trim)

def bytes_check(p: object) -> bool:
    """Return True if ``p`` is :class:`bytes` or a subtype (``PyBytes_Check``)."""
    ...

def bytes_check_exact(p: object) -> bool:
    """Return True if ``type(p) is bytes`` (``PyBytes_CheckExact``)."""
    ...

def bytes_contains(haystack: bytes, needle: bytes) -> bool:
    """Return True if ``needle`` is in ``haystack``.

    Notes
    -----
    Uses ``memchr``/``memmem`` under 256B, else the builtin ``in`` path.
    """
    ...

def bytes_bytearray_eq(a: object, b: object) -> bool:
    """Return True if ``bytes``/``bytearray`` contents match.

    Notes
    -----
    Either argument order is accepted; compares with ``memcmp`` after a length
    gate.
    """
    ...

def bytes_eq(a: bytes, b: bytes) -> bool:
    """Return True if ``a == b``.

    Notes
    -----
    Identity/len short-circuit plus ``memcmp`` on typed ``bytes``.
    """
    ...

def bytes_ne(a: bytes, b: bytes) -> bool:
    """Return True if ``a != b`` (inverse of ``bytes_eq``)."""
    ...

def bytes_startswith(s: bytes, prefix: bytes) -> bool:
    """Return True if typed ``s`` begins with ``prefix``.

    Notes
    -----
    Length gate plus ``memcmp`` on the typed prefix region.
    """
    ...

def bytes_endswith(s: bytes, suffix: bytes) -> bool:
    """Return True if typed ``s`` ends with ``suffix``.

    Notes
    -----
    Length gate plus tail ``memcmp`` on the typed suffix region.
    """
    ...

def bytes_from_object(o: object) -> bytes:
    """Return ``bytes`` from a buffer-protocol object (``PyBytes_FromObject``)."""
    ...

def bytes_len(b: bytes) -> int:
    """Return ``len(b)`` via ``PyBytes_GET_SIZE``."""
    ...

def bytes_size(b: object) -> int:
    """Return ``len(b)`` via checked ``PyBytes_Size``.

    Notes
    -----
    Prefer ``bytes_len`` on a typed ``bytes`` hot path.
    """
    ...
