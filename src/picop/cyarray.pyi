"""Typed helpers for :class:`array.array` buffers.

Prefer :mod:`picop.cyarray` (or starters in :mod:`picop.hot`) when the concrete
array type is known. See :doc:`/user_guide/quickstart` for import patterns.
"""

from array import array

# Preferred public names (0.3 hard trim)

def array_check(p: object) -> bool:
    """Return True if ``p`` is an :class:`array.array` (``isinstance``)."""
    ...

def array_check_exact(p: object) -> bool:
    """Return True if ``type(p) is array.array``."""
    ...

def array_clone(template: array, length: int, zero: bool = True) -> array:
    """Return a new array like ``template`` with ``length`` items.

    Notes
    -----
    Optionally zero-fills the new buffer when ``zero`` is true.
    """
    ...

def array_copy(a: array) -> array:
    """Return a shallow copy of ``a`` via Cython ``array.copy``."""
    ...

def array_extend(self: array, other: array) -> int:
    """Extend ``self`` from ``other`` via Cython ``array.extend``.

    Notes
    -----
    Requires the same typecode. Returns ``0`` on success and ``-1`` on error;
    errors raise. Do not use the status int as a bool.
    """
    ...

def array_len(a: array) -> int:
    """Return ``len(a)`` via ``Py_SIZE``."""
    ...

def array_eq(a: array, b: array) -> bool:
    """Return True if typed ``array.array`` values are equal.

    Notes
    -----
    Mixed Tier A parity: 0.59x (3.14), 1.00x (3.14t), 0.56x (3.15), 0.78x (3.15t);
    the typed Cython call site.

    Compares typecode/len then ``memcmp``.
    """
    ...

def array_ne(a: array, b: array) -> bool:
    """Return True if typed ``array.array`` values differ (``not array_eq``).

    Notes
    -----
    Mixed Tier A parity: 0.56x (3.14), 0.93x (3.14t), 0.53x (3.15), 0.74x (3.15t);
    the typed Cython call site.
    """
    ...

def array_resize(a: array, n: int) -> int:
    """Resize ``a`` to ``n`` elements via Cython ``array.resize``.

    Notes
    -----
    Returns ``0`` on success and ``-1`` on error; errors raise. Do not use the
    status int as a bool.
    """
    ...

def array_resize_smart(a: array, n: int) -> int:
    """Resize ``a`` to ``n`` via Cython ``array.resize_smart``.

    Notes
    -----
    Small-grow friendly. Returns ``0`` on success and ``-1`` on error; errors
    raise. Do not use the status int as a bool.
    """
    ...

def array_zero(a: array) -> int:
    """Zero all elements of ``a`` via ``memset``.

    Notes
    -----
    Returns ``0`` on success; errors raise. Do not use the status int as a
    bool.
    """
    ...
