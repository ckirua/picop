"""Complex construction, field access, and equality via ``PyComplex_*``.

Prefer builtins for ordinary complex arithmetic from Python. Use these on
known-type hot paths that need C-API field access. See
:doc:`/user_guide/quickstart`.
"""

def complex_check(p: object) -> bool:
    """Return True if ``p`` is a :class:`complex` or subtype (``PyComplex_Check``)."""
    ...

def complex_check_exact(p: object) -> bool:
    """Return True if ``type(p) is complex`` (``PyComplex_CheckExact``)."""
    ...

def complex_eq(a: object, b: object) -> bool:
    """Return True if values are equal with Python complex parity.

    Notes
    -----
    NaN on either real or imag part yields unequal (CPython parity).
    """
    ...

def complex_from_doubles(real: float, imag: float) -> object:
    """Return ``complex(real, imag)`` via ``PyComplex_FromDoubles``."""
    ...

def complex_real_as_double(op: object) -> float:
    """Return the real part of ``op`` as a C ``double`` (``PyComplex_RealAsDouble``)."""
    ...

def complex_imag_as_double(op: object) -> float:
    """Return the imaginary part of ``op`` as a C ``double`` (``PyComplex_ImagAsDouble``)."""
    ...
