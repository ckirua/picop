"""Public :mod:`picop.cytuple` stubs (signatures + docstrings for IDE / typecheckers)."""

# Preferred public names (0.3 hard trim)

def tuple_check(p: object) -> bool:
    """Return True if ``p`` is a :class:`tuple` or subtype (``PyTuple_Check``)."""
    ...

def tuple_check_exact(p: object) -> bool:
    """Return True if ``type(p) is tuple`` (``PyTuple_CheckExact``)."""
    ...

def tuple_get(t: tuple[object, ...], i: int) -> object:
    """Return ``t[i]`` via ``PyTuple_GET_ITEM``."""
    ...

def tuple_get_checked(t: tuple[object, ...], i: int) -> object:
    """Return ``t[i]`` via bounds-checked ``PyTuple_GetItem`` (raises ``IndexError``)."""
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
    """Return ``len(t)`` via checked ``PyTuple_Size`` (prefer ``tuple_len`` in hot paths)."""
    ...

def tuple_slice(t: tuple[object, ...], low: int, high: int) -> tuple[object, ...]:
    """Return ``t[low:high]`` as a new tuple via ``PyTuple_GetSlice``."""
    ...
