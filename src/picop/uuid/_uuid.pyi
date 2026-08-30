"""C-backed :class:`UUID` values and helpers compatible with :mod:`uuid`.

Prefer :func:`uuid4` / :func:`uuid4_bytes` on hot paths that only need random
v4 values. The :class:`UUID` type mirrors :class:`uuid.UUID` field layout and
formatting while constructing from canonical text or 16 raw bytes in C.
See :doc:`/user_guide/quickstart` for import patterns.
"""

import uuid
from types import NotImplementedType


class UUID(uuid.UUID):
    """Stdlib-compatible UUID built from canonical text or 16 bytes in C.

    Notes
    -----
    Field layout, ``str``/``hex``/``urn`` formatting, and comparisons match
    :class:`uuid.UUID`. Construction accepts a hyphenated/ canonical string or
    exactly 16 bytes; invalid input raises ``ValueError``.
    """

    def __init__(self, inp: str | bytes) -> None:
        """Construct from a UUID string or 16-byte binary form."""
        ...

    @property
    def bytes(self) -> bytes:
        """Return the 16-byte big-endian binary representation."""
        ...

    @property
    def bytes_le(self) -> bytes:
        """Return the 16-byte little-endian binary representation."""
        ...

    @property
    def int(self) -> int:
        """Return the 128-bit integer value of the UUID."""
        ...

    @property
    def hex(self) -> str:
        """Return the 32-character hexadecimal form without hyphens."""
        ...

    @property
    def fields(self) -> tuple[int, int, int, int, int, int]:
        """Return the six RFC 4122 integer fields as a tuple."""
        ...

    @property
    def time_low(self) -> int:
        """Return the ``time_low`` field (32 bits)."""
        ...

    @property
    def time_mid(self) -> int:
        """Return the ``time_mid`` field (16 bits)."""
        ...

    @property
    def time_hi_version(self) -> int:
        """Return the ``time_hi_and_version`` field (16 bits)."""
        ...

    @property
    def clock_seq_hi_variant(self) -> int:
        """Return the ``clock_seq_hi_and_reserved`` field (8 bits)."""
        ...

    @property
    def clock_seq_low(self) -> int:
        """Return the ``clock_seq_low`` field (8 bits)."""
        ...

    @property
    def time(self) -> int:
        """Return the 60-bit timestamp field when applicable."""
        ...

    @property
    def clock_seq(self) -> int:
        """Return the 14-bit clock sequence field."""
        ...

    @property
    def node(self) -> int:
        """Return the 48-bit node (MAC) field."""
        ...

    @property
    def urn(self) -> str:
        """Return the RFC 4122 ``urn:uuid:…`` form."""
        ...

    @property
    def variant(self) -> str:
        """Return the UUID variant name string (e.g. ``specified in RFC 4122``)."""
        ...

    @property
    def version(self) -> int | None:
        """Return the UUID version number, or ``None`` if not RFC 4122."""
        ...

    @property
    def is_safe(self) -> uuid.SafeUUID:
        """Return multiprocessing safety as :class:`uuid.SafeUUID`."""
        ...

    def __str__(self) -> str:
        """Return the canonical 8-4-4-4-12 hyphenated string form."""
        ...

    def __format__(self, format_spec: str) -> str:
        """Format like :meth:`uuid.UUID.__format__` (``s`` / ``x`` / ``X`` / empty)."""
        ...

    def __repr__(self) -> str:
        """Return a ``UUID('…')`` developer representation."""
        ...

    def __reduce__(self) -> tuple[type[UUID], tuple[bytes]]:
        """Return pickle state as ``(UUID, (bytes,))``."""
        ...

    def __eq__(self, other: object) -> bool | NotImplementedType:
        """Return True when ``other`` is a UUID with the same 128-bit value."""
        ...

    def __ne__(self, other: object) -> bool | NotImplementedType:
        """Return True when ``other`` is a UUID with a different 128-bit value."""
        ...

    def __lt__(self, other: object) -> bool | NotImplementedType:
        """Order by integer value against another UUID."""
        ...

    def __gt__(self, other: object) -> bool | NotImplementedType:
        """Order by integer value against another UUID."""
        ...

    def __le__(self, other: object) -> bool | NotImplementedType:
        """Order by integer value against another UUID."""
        ...

    def __ge__(self, other: object) -> bool | NotImplementedType:
        """Order by integer value against another UUID."""
        ...

    def __hash__(self) -> int:
        """Hash by the 128-bit integer value."""
        ...

    def __int__(self) -> int:
        """Return the 128-bit integer value (same as :attr:`int`)."""
        ...


def uuid4_bytes() -> bytes:
    """Return 16 random bytes with UUID v4 and RFC variant bits set.

    Notes
    -----
    Prefer when you only need the binary form and want to avoid allocating a
    :class:`UUID` object.
    """
    ...


def uuid4() -> UUID:
    """Return a random version 4 UUID.

    Notes
    -----
    Equivalent to wrapping :func:`uuid4_bytes` in :class:`UUID`.
    """
    ...
