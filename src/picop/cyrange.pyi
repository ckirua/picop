"""Typed equality helper for :class:`range`.

Prefer :mod:`picop.cyrange` when both sides are known ranges; otherwise use
builtin ``==``. See :doc:`/user_guide/quickstart` for import patterns.
"""

def range_eq(a: object, b: object) -> bool:
    """Return True if ranges represent the same sequence.

    Notes
    -----
    Mixed Tier A parity: 0.50x (3.15: identity), 0.54x (3.14: identity), 0.73x
    (3.14: ne span), 0.74x (3.15: eq empty), 0.74x (3.15: ne span), 0.75x (3.14: eq
    empty), 0.77x (3.14: eq span), 0.78x (3.15: eq large), 0.78x (3.14: eq equiv
    step), 0.78x (3.15: eq reversed), 0.78x (3.15: eq span), 0.79x (3.15: eq equiv
    step), 0.79x (3.14: eq large), 0.89x (3.14: ne step), 0.89x (3.14: eq reversed),
    1.23x (3.15: ne step); range-protocol bridge.

    Identity short-circuit plus richcompare — same semantics as
    ``range.__eq__``.
    """
    ...
