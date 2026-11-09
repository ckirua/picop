"""Float checks and equality with CPython float parity.

Prefer builtins for ordinary float work from Python. Tier A losers remain
``cpdef`` and carry a parity note in the stub. See
:doc:`/user_guide/quickstart`.
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

def float_as_double(pyfloat: object) -> float:
    """Return the C ``double`` of a Python float (``PyFloat_AsDouble``).

    Notes
    -----
    Slower than the plain-Python equivalent ``float(x)`` (Tier A 1.30–1.40x); hands
    Cython a C ``double``.
    """
    ...

def float_from_double(v: float) -> object:
    """Return a Python float from a C ``double`` (``PyFloat_FromDouble``).

    Notes
    -----
    Slower than the plain-Python equivalent ``float(x)`` (Tier A 1.34x); hands
    Cython a C ``double``.
    """
    ...

def float_from_cstr(s: object) -> object:
    """Return a float parsed from a ``str``/``bytes`` object (``PyFloat_FromString``)."""
    ...
