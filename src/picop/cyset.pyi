"""Typed C-API helpers for :class:`set` / :class:`frozenset` hot paths.

Prefer :mod:`picop.cyset` (or starters in :mod:`picop.hot`) when the concrete
set type is known; use protocol helpers only for unknown containers. Tier A
losers (ratio > 1.02 vs Python) are omitted from stubs but remain ``cpdef``.
See :doc:`/user_guide/quickstart` for import patterns.
"""

# Preferred public names (0.3 hard trim)

def set_add(s: set, value: object) -> int:
    """Add ``value`` via ``PySet_Add``.

    Notes
    -----
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
    """Return True if typed sets are equal (identity/size short-circuit + richcompare)."""
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
    Returns ``0`` on success; errors raise. Do not use the status int as a
    bool.
    """
    ...
