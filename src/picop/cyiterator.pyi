"""Iterator-protocol check and identity equality via ``PyIter_*``.

Prefer builtins for ordinary iteration from Python. Tier A losers remain
``cpdef`` but are omitted from stubs. See :doc:`/user_guide/quickstart`.
"""

def iter_check(o: object) -> bool:
    """Return True if ``o`` supports the iterator protocol (``PyIter_Check``)."""
    ...

def iter_eq(a: object, b: object) -> bool:
    """Return True if ``a is b`` (iterator identity; typical CPython ``object.__eq__``)."""
    ...
