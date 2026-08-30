"""Float checks and equality with CPython float parity.

Prefer builtins for ordinary float work from Python. Tier A losers remain
``cpdef`` but are omitted from stubs. See :doc:`/user_guide/quickstart`.
"""

def float_check(p: object) -> bool:
    """Return True if ``p`` is a :class:`float` or subtype (``PyFloat_Check``)."""
    ...

def float_check_exact(p: object) -> bool:
    """Return True if ``type(p) is float`` (``PyFloat_CheckExact``)."""
    ...

def float_eq(a: object, b: object) -> bool:
    """Return True if values are equal with Python float parity.

    Notes
    -----
    Matches CPython: ``NaN != NaN``, and ``+0.0 == -0.0``.
    """
    ...
