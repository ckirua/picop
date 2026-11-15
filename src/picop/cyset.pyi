"""Typed C-API helpers for :class:`set` / :class:`frozenset` hot paths.

Prefer :mod:`picop.cyset` (or starters in :mod:`picop.hot`) when the concrete
set type is known; use protocol helpers only for unknown containers. Tier A
losers (ratio > 1.02 vs Python) remain ``cpdef`` and carry a parity note. See
:doc:`/user_guide/quickstart` for import patterns.
"""

# Preferred public names (0.3 hard trim)

def set_add(s: set, value: object) -> int:
    """Add ``value`` via ``PySet_Add``.

    Notes
    -----
    Slower than the plain-Python equivalent ``s.add(v)`` (Tier A 1.03–1.06x);
    unchecked set mutation.

    Returns ``0`` on success; errors raise. Do not use the status int as a
    bool.
    """
    ...

def set_any_check(p: object) -> bool:
    """Return True if ``p`` is a set or frozenset (or subtype)."""
    ...

def set_any_check_exact(p: object) -> bool:
    """Return True if ``type(p) is set`` or ``frozenset`` (no subtype)."""
    ...

def set_check(p: object) -> bool:
    """Return True if ``p`` is a :class:`set` or subtype (``PySet_Check``)."""
    ...

def set_check_exact(p: object) -> bool:
    """Return True if ``type(p) is set`` (``PySet_CheckExact``)."""
    ...

def set_clear(s: set) -> int:
    """Clear ``s`` via ``PySet_Clear``.

    Notes
    -----
    Mixed Tier A parity: 1.09x (3.14), 1.02x (3.14t), 1.02x (3.15), 1.07x (3.15t);
    unchecked set mutation.

    Returns ``0`` on success; errors raise. Do not use the status int as a
    bool.
    """
    ...

def set_contains(anyset: object, value: object) -> bool:
    """Return whether ``value`` is in ``anyset`` via ``PySet_Contains``."""
    ...

def set_copy(s: set) -> set:
    """Shallow-copy ``s`` via ``PySet_New(s)``."""
    ...

def set_discard(s: set, value: object) -> int:
    """Discard ``value`` via ``PySet_Discard``.

    Notes
    -----
    Mixed Tier A parity: 1.06x (3.14), 1.03x (3.14t), 1.01x (3.15), 1.04x (3.15t);
    unchecked set mutation.

    Returns ``1`` if removed, ``0`` if absent (no ``KeyError``). Errors raise.
    Do not treat the status int as a plain bool for success/failure.
    """
    ...

def set_empty() -> set:
    """Return a new empty set via ``PySet_New(NULL)``."""
    ...

def frozenset_check(p: object) -> bool:
    """Return True if ``p`` is a :class:`frozenset` or subtype."""
    ...

def frozenset_check_exact(p: object) -> bool:
    """Return True if ``type(p) is frozenset``."""
    ...

def frozenset_empty() -> frozenset:
    """Return a new empty frozenset via ``PyFrozenSet_New(NULL)``."""
    ...

def frozenset_new(iterable: object) -> frozenset:
    """Return a new frozenset from ``iterable`` via ``PyFrozenSet_New``."""
    ...

def frozenset_eq(a: frozenset, b: frozenset) -> bool:
    """Return True if typed frozensets are equal (identity/size short-circuit + richcompare)."""
    ...

def set_len(s: set) -> int:
    """Return ``len(s)`` via ``PySet_GET_SIZE`` (exact ``set``)."""
    ...

def set_eq(a: set, b: set) -> bool:
    """Return True if typed sets are equal (identity/size short-circuit + richcompare).

    Notes
    -----
    Mixed Tier A parity: 0.83x (3.14), 1.25x (3.14t), 0.79x (3.15), 1.03x (3.15t);
    unchecked set mutation.
    """
    ...

def set_new(iterable: object) -> set:
    """Return a new set from ``iterable`` via ``PySet_New``."""
    ...

def set_size(anyset: object) -> int:
    """Return ``len(anyset)`` via checked ``PySet_Size``.

    Notes
    -----
    Accepts set/frozenset/subtypes. Prefer ``set_len`` on a typed exact
    ``set`` hot path.
    """
    ...

def set_update(s: set, iterable: object) -> int:
    """Update ``s`` from ``iterable`` via ``_PySet_Update``.

    Notes
    -----
    Mixed Tier A parity: 1.05x (3.14), 1.10x (3.14t), 1.01x (3.15), 1.12x (3.15t);
    unchecked set mutation.

    Returns ``0`` on success; errors raise. Do not use the status int as a
    bool.
    """
    ...

def set_pop(s: set) -> object:
    """Return and remove an arbitrary element of ``s`` (``PySet_Pop``).

    Notes
    -----
    Slower than the plain-Python equivalent ``s.pop()`` (Tier A 1.03–1.15x);
    unchecked set mutation.
    """
    ...
