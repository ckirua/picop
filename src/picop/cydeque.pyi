"""Typed equality helper for :class:`collections.deque`.

Prefer :mod:`picop.cydeque` when both sides are known deques; otherwise use
builtin ``==``. See :doc:`/user_guide/quickstart` for import patterns.
"""

def deque_eq(a: object, b: object) -> bool:
    """Return True if deques are equal.

    Notes
    -----
    Identity short-circuit plus richcompare — same semantics as
    ``deque.__eq__``.
    """
    ...
