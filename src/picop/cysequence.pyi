"""Abstract sequence-protocol helpers via the CPython C-API.

Use when the concrete type is unknown. Prefer typed ``list_*`` / ``tuple_*``
from Core or :mod:`picop.hot` when the type is known. Tier A losers remain
``cpdef`` and carry a parity note in the stub. See :doc:`/user_guide/safety`.
"""

def seq_check(o: object) -> bool:
    """Return True if ``o`` supports the sequence protocol (``PySequence_Check``)."""
    ...

def seq_concat(o1: object, o2: object) -> object:
    """Return ``o1 + o2`` via ``PySequence_Concat``."""
    ...

def seq_contains(o: object, value: object) -> bool:
    """Return ``value in o`` via ``PySequence_Contains``."""
    ...

def seq_del(o: object, i: int) -> int:
    """Delete ``o[i]`` via ``PySequence_DelItem``.

    Notes
    -----
    Returns ``0`` on success; errors raise — do not use the status as a bool.
    """
    ...

def seq_eq(a: object, b: object) -> bool:
    """Return True if sequences are equal via identity/size short-circuit + richcompare.

    Notes
    -----
    Prefer ``list_eq`` / ``tuple_eq`` when both operands are typed.
    """
    ...

def seq_del_slice(o: object, i1: int, i2: int) -> int:
    """Delete ``o[i1:i2]`` via ``PySequence_DelSlice``.

    Notes
    -----
    Returns ``0`` on success; errors raise — do not use the status as a bool.
    """
    ...

def seq_get(o: object, i: int) -> object:
    """Return ``o[i]`` via ``PySequence_GetItem``."""
    ...

def seq_index(o: object, value: object) -> int:
    """Return ``o.index(value)`` via ``PySequence_Index``."""
    ...

def seq_inplace_concat(o1: object, o2: object) -> object:
    """Return ``o1 += o2`` result via ``PySequence_InPlaceConcat``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a += b`` (Tier A 1.02x); works on any
    sequence, not just ``list``.
    """
    ...

def seq_inplace_repeat(o: object, count: int) -> object:
    """Return ``o *= count`` result via ``PySequence_InPlaceRepeat``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a *= b`` (Tier A 1.06x); works on any
    sequence, not just ``list``.
    """
    ...

def seq_list(o: object) -> list:
    """Return ``list(o)`` via ``PySequence_List`` (always a new list)."""
    ...

def seq_repeat(o: object, count: int) -> object:
    """Return ``o * count`` via ``PySequence_Repeat``."""
    ...

def seq_set(o: object, i: int, v: object) -> int:
    """Assign ``o[i] = v`` via ``PySequence_SetItem``.

    Notes
    -----
    Returns ``0`` on success; errors raise — do not use the status as a bool.
    """
    ...

def seq_set_slice(o: object, i1: int, i2: int, v: object) -> int:
    """Assign ``o[i1:i2] = v`` via ``PySequence_SetSlice``.

    Notes
    -----
    Returns ``0`` on success; errors raise — do not use the status as a bool.
    """
    ...

def seq_slice(o: object, i1: int, i2: int) -> object:
    """Return ``o[i1:i2]`` via ``PySequence_GetSlice``.

    Notes
    -----
    Slower than the plain-Python equivalent ``x[a:b]`` (Tier A 1.16x); works on any
    sequence, not just ``list``.
    """
    ...

def seq_tuple(o: object) -> tuple:
    """Return ``tuple(o)`` via ``PySequence_Tuple``.

    Notes
    -----
    Slower than the plain-Python equivalent ``tuple(x)`` (Tier A 1.08x); works on
    any sequence, not just ``list``.
    """
    ...

def seq_count(o: object, value: object) -> int:
    """Return the number of occurrences of ``value`` in sequence ``o`` (``PySequence_Count``)."""
    ...

def seq_len(o: object) -> int:
    """Return the length of sequence ``o`` (``PySequence_Length``).

    Notes
    -----
    Slower than the plain-Python equivalent ``len(x)`` (Tier A 1.15x); works on any
    sequence, not just ``list``.
    """
    ...

def seq_size(o: object) -> int:
    """Return the size of sequence ``o`` (``PySequence_Size``, alias of ``PySequence_Length``).

    Notes
    -----
    Slower than the plain-Python equivalent ``len(x)`` (Tier A 1.15x); works on any
    sequence, not just ``list``.
    """
    ...
