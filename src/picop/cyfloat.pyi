"""Float checks and equality with CPython float parity.

Prefer builtins for ordinary float work from Python. Tier A losers remain
``cpdef`` and carry a parity note in the stub. See
:doc:`/user_guide/quickstart`.
"""

def float_check(p: object) -> bool:
    """Return True if ``p`` is a :class:`float` or subtype (``PyFloat_Check``)."""
    ...

def float_check_exact(p: object) -> bool:
    """Return True if ``type(p) is float`` (``PyFloat_CheckExact``)."""
    ...

def float_eq(a: object, b: object) -> bool:
    """Return True if values are equal with Python float parity.

    Notes
    -----
    Matches CPython: ``NaN != NaN``, and ``+0.0 == -0.0``.
    """
    ...

def float_as_double(pyfloat: object) -> float:
    """Return the C ``double`` of a Python float (``PyFloat_AsDouble``).

    Notes
    -----
    Slower than the plain-Python equivalent ``float(x)`` (Tier A 1.40–1.51x); hands
    Cython a C ``double``.
    """
    ...

def float_from_double(v: float) -> object:
    """Return a Python float from a C ``double`` (``PyFloat_FromDouble``).

    Notes
    -----
    Slower than the plain-Python equivalent ``float(x)`` (Tier A 1.46x); hands
    Cython a C ``double``.
    """
    ...

def float_from_cstr(s: object) -> object:
    """Return a float parsed from a ``str``/``bytes`` object (``PyFloat_FromString``).

    Notes
    -----
    Slower than the plain-Python equivalent ``float(x)`` (Tier A 1.02x); hands
    Cython a C ``double``.
    """
    ...

def float_pack8(value: float, little_endian: bool = True) -> bytes:
    """Pack a C double into 8 bytes using the selected byte order."""
    ...

def float_pack4(value: float, little_endian: bool = True) -> bytes:
    """Pack a C double into 4 bytes (rounded to float precision)."""
    ...

def float_pack2(value: float, little_endian: bool = True) -> bytes:
    """Pack a C double into IEEE half precision."""
    ...

def float_unpack8(data: bytes, little_endian: bool = True) -> float:
    """Unpack exactly 8 bytes; reject short buffers before raw-pointer access."""
    ...

def float_unpack4(data: bytes, little_endian: bool = True) -> float:
    """Unpack exactly 4 bytes; reject short buffers before raw-pointer access."""
    ...

def float_unpack2(data: bytes, little_endian: bool = True) -> float:
    """Unpack exactly 2 bytes; reject short buffers before raw-pointer access."""
    ...
