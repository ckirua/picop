"""Hashing helpers for raw buffers and object pointers (CPython 3.8+)."""

def hash_buffer(data: object, start: int = 0, end: int = -1) -> int:
    """Return the CPython hash of ``data``'s bytes, or of the ``data[start:end]`` range.

    Notes
    -----
    Mixed Tier A parity: 0.39x (3.15: array.array('B') n=6), 0.42x (3.14:
    array.array('B') n=6), 0.45x (3.15: bytearray n=64), 0.48x (3.14: bytearray
    n=64), 0.50x (3.14: memoryview n=256 range 64:128), 0.51x (3.15: memoryview
    n=256 range 64:128), 0.57x (3.14: bytes n=2048 range 64:128), 0.58x (3.15: bytes
    n=2048 range 64:128), 0.77x (3.15: bytearray n=2048), 0.78x (3.14: bytearray
    n=2048), 1.46x (3.14: bytes n=8 (cached)), 1.63x (3.15: bytes n=8 (cached)),
    2.85x (3.14: memoryview n=256 (cached)), 3.08x (3.15: memoryview n=256
    (cached)); re-hashes the buffer every call, while ``bytes``/``memoryview`` cache
    theirs.

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
