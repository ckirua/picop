"""Typed C-API helpers for :class:`tuple` hot paths.

Prefer :mod:`picop.cytuple` (or starters in :mod:`picop.hot`) over builtin
``tuple`` access when the concrete type is known. Unchecked getters are
trusted-caller tools — see :doc:`/user_guide/safety`. Import patterns:
:doc:`/user_guide/quickstart`.
"""

# Preferred public names (0.3 hard trim)

def tuple_check(p: object) -> bool:
    """Return True if ``p`` is a :class:`tuple` or subtype (``PyTuple_Check``)."""
    ...

def tuple_check_exact(p: object) -> bool:
    """Return True if ``type(p) is tuple`` (``PyTuple_CheckExact``)."""
    ...

def tuple_get(t: tuple[object, ...], i: int) -> object:
    """Return ``t[i]`` via ``PyTuple_GET_ITEM``.

    Notes
    -----
    Unchecked: out-of-bounds is undefined behavior. Prefer
    ``tuple_get_checked`` when the index may be OOB, or bound the index
    yourself before calling.
    """
    ...

def tuple_get_checked(t: tuple[object, ...], i: int) -> object:
    """Return ``t[i]`` via bounds-checked ``PyTuple_GetItem``.

    Notes
    -----
    Raises ``IndexError`` on out-of-bounds (unlike unchecked ``tuple_get``).
    """
    ...

def tuple_len(t: tuple[object, ...]) -> int:
    """Return ``len(t)`` via ``PyTuple_GET_SIZE``."""
    ...

def tuple_eq(a: tuple, b: tuple) -> bool:
    """Return True if typed tuples are equal (identity/len + richcompare)."""
    ...

def tuple_pack2(a: object, b: object) -> tuple[object, object]:
    """Return ``(a, b)`` via ``PyTuple_Pack``."""
    ...

def tuple_pack3(a: object, b: object, c: object) -> tuple[object, object, object]:
    """Return ``(a, b, c)`` via ``PyTuple_Pack``."""
    ...

def tuple_pack4(
    a: object, b: object, c: object, d: object
) -> tuple[object, object, object, object]:
    """Return ``(a, b, c, d)`` via ``PyTuple_Pack``."""
    ...

def tuple_size(t: tuple[object, ...]) -> int:
    """Return ``len(t)`` via checked ``PyTuple_Size``.

    Notes
    -----
    Prefer ``tuple_len`` on typed hot paths.
    """
    ...

def tuple_slice(t: tuple[object, ...], low: int, high: int) -> tuple[object, ...]:
    """Return ``t[low:high]`` as a new tuple via ``PyTuple_GetSlice``."""
    ...
