"""Bool construction and checks wrapping ``PyBool_*``.

Prefer builtins for ordinary Python code; use these on known-type hot paths
that need C-API parity. See :doc:`/user_guide/quickstart`.
"""

def bool_check(o: object) -> bool:
    """Return True if ``o`` is a :class:`bool` (``PyBool_Check``)."""
    ...

def bool_eq(a: object, b: object) -> bool:
    """Return True if values are equal (identity short-circuit + richcompare)."""
    ...

def bool_from_long(v: int) -> object:
    """Return ``True`` or ``False`` via ``PyBool_FromLong`` (nonzero → True).

    Notes
    -----
    Mixed Tier A parity: 1.01x (3.15: 1→True), 1.09x (3.14: 0→False), 1.16x (3.14:
    1→True), 1.17x (3.15: 0→False); returns the C ``bool`` for a Cython ``int``.
    """
    ...

def bool_true() -> object:
    """Return ``True`` via ``PyBool_FromLong(1)``."""
    ...

def bool_false() -> object:
    """Return ``False`` via ``PyBool_FromLong(0)``."""
    ...
