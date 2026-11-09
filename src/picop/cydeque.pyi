"""Typed equality helper for :class:`collections.deque`.

Prefer :mod:`picop.cydeque` when both sides are known deques; otherwise use
builtin ``==``. See :doc:`/user_guide/quickstart` for import patterns.
"""

def deque_eq(a: object, b: object) -> bool:
    """Return True if deques are equal.

    Notes
    -----
    Mixed Tier A parity: 0.59x (identity), 0.90x (eq empty), 0.92x (eq nested),
    0.92x (ne small), 0.93x (eq small), 0.98x (ne n=64), 1.08x (eq n=64); the typed
    Cython call site.

    Identity short-circuit plus richcompare — same semantics as
    ``deque.__eq__``.
    """
    ...
