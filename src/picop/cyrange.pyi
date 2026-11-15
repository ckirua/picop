"""Typed equality helper for :class:`range`.

Prefer :mod:`picop.cyrange` when both sides are known ranges; otherwise use
builtin ``==``. See :doc:`/user_guide/quickstart` for import patterns.
"""

def range_eq(a: object, b: object) -> bool:
    """Return True if ranges represent the same sequence.

    Notes
    -----
    Identity short-circuit plus richcompare — same semantics as
    ``range.__eq__``.
    """
    ...
