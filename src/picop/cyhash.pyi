"""Hashing helpers for raw buffers and object pointers (CPython 3.8+)."""

def hash_buffer(data: object, start: int = 0, end: int = -1) -> int:
    """Return the CPython hash of ``data``'s bytes, or of the ``data[start:end]`` range.

    Notes
    -----
    Mixed Tier A parity: 0.76x (3.14), 0.89x (3.14t), 0.78x (3.15), 0.78x (3.15t);
    re-hashes the buffer every call, while ``bytes``/``memoryview`` cache theirs.

    Accepts any simple buffer object (``bytes``, ``bytearray``, ``memoryview`` and
    exporters such as arrays); ``str`` is not a buffer and raises ``TypeError``.
    ``bytearray`` and ``array.array`` have no ``__hash__``, and hashing a writable
    ``memoryview`` raises ``ValueError``, so this replaces ``hash(bytes(data))``
    without the copy. Once a ``bytes`` or read-only ``memoryview`` has been hashed the
    builtin is cheaper: the value is cached on the object. ``start`` defaults to 0 and
    any negative ``end`` means the end of the buffer; ``start``/``end`` out of range or
    ``end < start`` raise ``ValueError``. The value matches
    ``hash(bytes(data[start:end]))`` exactly (SipHash over the same bytes).
    """
    ...
