"""Integer (``PyLong``) conversion and checks for known-type hot paths.

Prefer builtins for ordinary arithmetic from Python. Tier A losers remain
``cpdef`` but are omitted from stubs. Mask helpers wrap on overflow without
raising — trusted-caller. See :doc:`/user_guide/safety`.
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
    """Return an :class:`int` from an unsigned long via ``PyLong_FromUnsignedLong``."""
    ...

def long_from_size(v: int) -> object:
    """Return an :class:`int` from ``size_t`` via ``PyLong_FromSize_t``."""
    ...

def long_from_longlong(v: int) -> object:
    """Return an :class:`int` from ``long long`` via ``PyLong_FromLongLong``."""
    ...

def long_from_ulonglong(v: int) -> object:
    """Return an :class:`int` from ``unsigned long long`` via ``PyLong_FromUnsignedLongLong``."""
    ...

def long_as_long_overflow(pylong: object) -> tuple[int, int]:
    """Return ``(value, overflow)`` via ``PyLong_AsLongAndOverflow``."""
    ...

def long_as_ulong(pylong: object) -> int:
    """Return an unsigned long via ``PyLong_AsUnsignedLong``."""
    ...

def long_as_longlong(pylong: object) -> int:
    """Return a ``long long`` via ``PyLong_AsLongLong``."""
    ...

def long_as_ulonglong(pylong: object) -> int:
    """Return an ``unsigned long long`` via ``PyLong_AsUnsignedLongLong``."""
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
