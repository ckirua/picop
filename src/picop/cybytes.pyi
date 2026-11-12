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

class BytesWriter:
    """Build a ``bytes`` object incrementally with CPython's internal writer.

    Notes
    -----
    Slower than the plain-Python equivalent ``b''.join(parts)`` (Tier A 3.32x)
    when the parts are already materialized; faster than ``bytearray``
    accumulation (Tier A 0.85x) and far faster than ``b += p``. Streaming
    niche: no part list is built. ``finish()``/``discard()`` close the
    writer; later calls raise ``RuntimeError``.
    """

    def __init__(self, max_size: int = 0) -> None:
        """Initialize an empty bytes writer; ``max_size`` is a capacity hint
        (effective on CPython 3.8-3.14, ignored on 3.15+)."""
        ...

    def write(self, data: bytes | bytearray) -> None:
        """Append ``data`` (bytes or bytearray) to the writer."""
        ...

    def write_char(self, ch: int) -> None:
        """Append a single byte ``0 <= ch <= 255``."""
        ...

    def finish(self) -> bytes:
        """Return the built bytes and close the writer."""
        ...

    def discard(self) -> None:
        """Release the writer's buffer without producing a result."""
        ...

    def __enter__(self) -> "BytesWriter":
        """Return the writer."""
        ...

    def __exit__(self, exc, value, tb) -> bool:
        """Discard the writer if it is still open."""
        ...
