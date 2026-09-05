"""Typed C-API helpers for :class:`list` hot paths.

Prefer :mod:`picop.cylist` (or starters in :mod:`picop.hot`) over builtin
``list`` methods when the concrete type is known. Unchecked getters are
trusted-caller tools — see :doc:`/user_guide/safety`. Import patterns:
:doc:`/user_guide/quickstart`.
"""

# Preferred public names (0.3 hard trim)

def list_append(l: list, value: object) -> int:
    """Append ``value`` via ``PyList_Append``.

    Notes
    -----
    Returns ``0`` on success and ``-1`` on error; errors raise. Do not use the
    status int as a bool.
    """
    ...

def list_as_tuple(l: list) -> tuple:
    """Return ``tuple(l)`` via ``PyList_AsTuple``."""
    ...

def list_check(p: object) -> bool:
    """Return True if ``p`` is a :class:`list` or subtype (``PyList_Check``)."""
    ...

def list_check_exact(p: object) -> bool:
    """Return True if ``type(p) is list`` (``PyList_CheckExact``)."""
    ...

def list_clear(l: list) -> int:
    """Clear ``l`` via ``PyList_Clear``.

    Notes
    -----
    Returns ``0`` on success and ``-1`` on error; errors raise. Do not use the
    status int as a bool.
    """
    ...

def list_copy(l: list) -> list:
    """Return a shallow copy of ``l`` via ``PyList_GetSlice``."""
    ...

def list_empty() -> list:
    """Return a new empty list via ``PyList_New(0)``."""
    ...

def list_extend(l: list, iterable: object) -> int:
    """Extend ``l`` from ``iterable`` via ``PyList_Extend``.

    Notes
    -----
    Returns ``0`` on success and ``-1`` on error; errors raise. Do not use the
    status int as a bool.
    """
    ...

def list_get(l: list, i: int) -> object:
    """Return ``l[i]`` via ``PyList_GET_ITEM``.

    Notes
    -----
    Unchecked: out-of-bounds is undefined behavior. Prefer
    ``list_get_checked`` / ``list_get_ref`` when the index may be OOB, or bound
    the index yourself before calling.
    """
    ...

def list_get_checked(l: list, i: int) -> object:
    """Return ``l[i]`` via bounds-checked ``PyList_GetItem``.

    Notes
    -----
    Raises ``IndexError`` on out-of-bounds (unlike unchecked ``list_get``).
    """
    ...

def list_get_ref(l: list, i: int) -> object:
    """Return a strong ref to ``l[i]`` via ``PyList_GetItemRef``.

    Notes
    -----
    Raises ``IndexError`` on out-of-bounds (unlike unchecked ``list_get``).
    """
    ...

def list_insert(l: list, i: int, value: object) -> int:
    """Insert ``value`` at ``i`` via ``PyList_Insert``.

    Notes
    -----
    Returns ``0`` on success and ``-1`` on error; errors raise. Do not use the
    status int as a bool.
    """
    ...

def list_len(l: list) -> int:
    """Return ``len(l)`` via ``PyList_GET_SIZE``."""
    ...

def list_eq(a: list, b: list) -> bool:
    """Return True if typed lists are equal (identity/len short-circuit + richcompare)."""
    ...


def list_reverse(l: list) -> int:
    """Reverse ``l`` in place via ``PyList_Reverse``.

    Notes
    -----
    Returns ``0`` on success and ``-1`` on error; errors raise. Do not use the
    status int as a bool.
    """
    ...

def list_set_item(l: list, i: int, value: object) -> int:
    """Set ``l[i] = value`` via ``PyList_SetItem``.

    Notes
    -----
    INCREFs ``value`` then steals the new reference into the list slot. Returns
    ``0`` on success and ``-1`` on error; errors raise. Do not use the status
    int as a bool.
    """
    ...

def list_set_slice(l: list, low: int, high: int, itemlist: object = None) -> int:
    """Assign ``l[low:high] = itemlist`` via ``PyList_SetSlice``.

    Notes
    -----
    Pass ``None`` for ``itemlist`` to delete the slice. Returns ``0`` on
    success and ``-1`` on error; errors raise. Do not use the status int as a
    bool.
    """
    ...

def list_size(l: object) -> int:
    """Return ``len(l)`` via checked ``PyList_Size``.

    Notes
    -----
    Prefer ``list_len`` on a typed ``list`` hot path.
    """
    ...

def list_slice(l: list, low: int, high: int) -> list:
    """Return ``l[low:high]`` via ``PyList_GetSlice``."""
    ...

def list_sort(l: list) -> int:
    """Sort ``l`` in place via ``PyList_Sort``.

    Notes
    -----
    Returns ``0`` on success and ``-1`` on error; errors raise. Do not use the
    status int as a bool.
    """
    ...
