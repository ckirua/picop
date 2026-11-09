"""Integer (``PyLong``) conversion and checks for known-type hot paths.

Prefer builtins for ordinary arithmetic from Python. Tier A losers remain
``cpdef`` and carry a parity note in the stub. Mask helpers wrap on overflow
without raising — trusted-caller. See :doc:`/user_guide/safety`.
"""

def long_check(p: object) -> bool:
    """Return True if ``p`` is an :class:`int` or subtype (``PyLong_Check``)."""
    ...

def long_check_exact(p: object) -> bool:
    """Return True if ``type(p) is int`` (``PyLong_CheckExact``); False for :class:`bool`."""
    ...

def long_eq(a: object, b: object) -> bool:
    """Return True if integers are equal (identity short-circuit + richcompare)."""
    ...

def int_eq(a: object, b: object) -> bool:
    """Return True if ``a == b`` — thin alias of ``long_eq`` (same semantics)."""
    ...

def long_from_ulong(v: int) -> object:
    """Return an :class:`int` from an unsigned long via ``PyLong_FromUnsignedLong``.

    Notes
    -----
    Slower than the plain-Python equivalent ``int(x)`` (Tier A 1.12x); hands Cython
    a C integer type.
    """
    ...

def long_from_size(v: int) -> object:
    """Return an :class:`int` from ``size_t`` via ``PyLong_FromSize_t``.

    Notes
    -----
    Slower than the plain-Python equivalent ``int(x)`` (Tier A 1.32x); hands Cython
    a C integer type.
    """
    ...

def long_from_longlong(v: int) -> object:
    """Return an :class:`int` from ``long long`` via ``PyLong_FromLongLong``.

    Notes
    -----
    Slower than the plain-Python equivalent ``int(x)`` (Tier A 1.74x); hands Cython
    a C integer type.
    """
    ...

def long_from_ulonglong(v: int) -> object:
    """Return an :class:`int` from ``unsigned long long`` via ``PyLong_FromUnsignedLongLong``.

    Notes
    -----
    Slower than the plain-Python equivalent ``int(x)`` (Tier A 1.78x); hands Cython
    a C integer type.
    """
    ...

def long_as_long_overflow(pylong: object) -> tuple[int, int]:
    """Return ``(value, overflow)`` via ``PyLong_AsLongAndOverflow``."""
    ...

def long_as_ulong(pylong: object) -> int:
    """Return an unsigned long via ``PyLong_AsUnsignedLong``.

    Notes
    -----
    Slower than the plain-Python equivalent ``int(x)`` (Tier A 1.23x); hands Cython
    a C integer type.
    """
    ...

def long_as_longlong(pylong: object) -> int:
    """Return a ``long long`` via ``PyLong_AsLongLong``.

    Notes
    -----
    Slower than the plain-Python equivalent ``int(x)`` (Tier A 2.31x); hands Cython
    a C integer type.
    """
    ...

def long_as_ulonglong(pylong: object) -> int:
    """Return an ``unsigned long long`` via ``PyLong_AsUnsignedLongLong``.

    Notes
    -----
    Slower than the plain-Python equivalent ``int(x)`` (Tier A 2.22x); hands Cython
    a C integer type.
    """
    ...

def long_as_ulong_mask(io: object) -> int:
    """Return ``PyLong_AsUnsignedLongMask``.

    Notes
    -----
    Wraps on overflow and does not raise — trusted-caller. See
    :doc:`/user_guide/safety`.
    """
    ...

def long_as_ulonglong_mask(io: object) -> int:
    """Return ``PyLong_AsUnsignedLongLongMask``.

    Notes
    -----
    Wraps on overflow and does not raise — trusted-caller. See
    :doc:`/user_guide/safety`.
    """
    ...

def long_as_double(pylong: object) -> float:
    """Return the C ``double`` of an integer (``PyLong_AsDouble``).

    Notes
    -----
    Slower than the plain-Python equivalent ``float(x)`` (Tier A 1.06x); hands
    Cython a C integer type.
    """
    ...

def long_as_long(pylong: object) -> int:
    """Return the C ``long`` of an integer (``PyLong_AsLong``)."""
    ...

def long_as_ssize(pylong: object) -> int:
    """Return the ``Py_ssize_t`` of an integer (``PyLong_AsSsize_t``).

    Notes
    -----
    Slower than the plain-Python equivalent ``int(x)`` (Tier A 1.15x); hands Cython
    a C integer type.
    """
    ...

def long_from_double(v: float) -> object:
    """Return a Python int from a C ``double`` (``PyLong_FromDouble``).

    Notes
    -----
    Slower than the plain-Python equivalent ``int(x)`` (Tier A 1.36x); hands Cython
    a C integer type.
    """
    ...

def long_from_long(v: int) -> object:
    """Return a Python int from a C ``long`` (``PyLong_FromLong``).

    Notes
    -----
    Slower than the plain-Python equivalent ``int(x)`` (Tier A 1.15x); hands Cython
    a C integer type.
    """
    ...

def long_from_ssize(v: int) -> object:
    """Return a Python int from a ``Py_ssize_t`` (``PyLong_FromSsize_t``).

    Notes
    -----
    Slower than the plain-Python equivalent ``int(x)`` (Tier A 1.10x); hands Cython
    a C integer type.
    """
    ...
