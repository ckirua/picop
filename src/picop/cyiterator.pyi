"""Iterator-protocol check and identity equality via ``PyIter_*``.

Prefer builtins for ordinary iteration from Python. Tier A losers remain
``cpdef`` and carry a parity note in the stub. See
:doc:`/user_guide/quickstart`.
"""

def iter_check(o: object) -> bool:
    """Return True if ``o`` supports the iterator protocol (``PyIter_Check``)."""
    ...

def iter_eq(a: object, b: object) -> bool:
    """Return True if ``a is b`` (iterator identity; typical CPython ``object.__eq__``)."""
    ...

def iter_next(o: object) -> object:
    """Return the next item of iterator ``o`` (``PyIter_Next``); ``None`` when exhausted.

    Notes
    -----
    Slower than the plain-Python equivalent ``next`` (Tier A 1.05x); iterator-
    protocol bridge.
    """
    ...
