"""Abstract number-protocol helpers via the CPython C-API.

Prefer builtins for binary/unary ops from Python; keep checks, ``num_eq``, and
measured wins here when the operand type is unknown. Tier A losers remain
``cpdef`` and carry a parity note in the stub. See
:doc:`/user_guide/quickstart`.
"""

def num_check(o: object) -> bool:
    """Return True if ``o`` provides the number protocol (``PyNumber_Check``)."""
    ...

def num_index_check(o: object) -> bool:
    """Return True if ``o`` is an index integer (``PyIndex_Check``)."""
    ...

def num_eq(a: object, b: object) -> bool:
    """Return True if ``a == b`` via richcompare (abstract number; NaN parity)."""
    ...

def num_floordiv(o1: object, o2: object) -> object:
    """Return ``o1 // o2`` via ``PyNumber_FloorDivide``.

    Notes
    -----
    Mixed Tier A parity: 0.96x (3.14), 1.05x (3.14t), 1.01x (3.15), 1.01x (3.15t);
    protocol bridge for unknown number types.
    """
    ...

def num_sub(o1: object, o2: object) -> object:
    """Return ``o1 - o2`` via ``PyNumber_Subtract``."""
    ...

def num_matmul(o1: object, o2: object) -> object:
    """Return ``o1 @ o2`` via ``PyNumber_MatrixMultiply``.

    Notes
    -----
    Mixed Tier A parity: 0.75x (3.14), 1.04x (3.14t), 0.99x (3.15), 1.03x (3.15t);
    protocol bridge for unknown number types.
    """
    ...

def num_divmod(o1: object, o2: object) -> object:
    """Return ``divmod(o1, o2)`` via ``PyNumber_Divmod``."""
    ...

def num_pos(o: object) -> object:
    """Return ``+o`` via ``PyNumber_Positive``."""
    ...

def num_invert(o: object) -> object:
    """Return ``~o`` via ``PyNumber_Invert``."""
    ...

def num_lshift(o1: object, o2: object) -> object:
    """Return ``o1 << o2`` via ``PyNumber_Lshift``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a << b`` (Tier A 1.04–1.47x); protocol
    bridge for unknown number types.
    """
    ...

def num_rshift(o1: object, o2: object) -> object:
    """Return ``o1 >> o2`` via ``PyNumber_Rshift``.

    Notes
    -----
    Mixed Tier A parity: 1.06x (3.14), 1.08x (3.14t), 0.99x (3.15), 1.38x (3.15t);
    protocol bridge for unknown number types.
    """
    ...

def num_xor(o1: object, o2: object) -> object:
    """Return ``o1 ^ o2`` via ``PyNumber_Xor``.

    Notes
    -----
    Mixed Tier A parity: 0.98x (3.14), 1.02x (3.14t), 0.99x (3.15), 1.01x (3.15t);
    protocol bridge for unknown number types.
    """
    ...

def num_or(o1: object, o2: object) -> object:
    """Return ``o1 | o2`` via ``PyNumber_Or``."""
    ...

def num_inplace_add(o1: object, o2: object) -> object:
    """Return in-place ``o1 += o2`` result via ``PyNumber_InPlaceAdd``."""
    ...

def num_inplace_sub(o1: object, o2: object) -> object:
    """Return in-place ``o1 -= o2`` result via ``PyNumber_InPlaceSubtract``.

    Notes
    -----
    Mixed Tier A parity: 1.02x (3.14), 0.94x (3.14t), 1.00x (3.15), 1.00x (3.15t);
    protocol bridge for unknown number types.
    """
    ...

def num_inplace_mul(o1: object, o2: object) -> object:
    """Return in-place ``o1 *= o2`` result via ``PyNumber_InPlaceMultiply``.

    Notes
    -----
    Mixed Tier A parity: 1.03x (3.14), 1.04x (3.14t), 1.00x (3.15), 0.98x (3.15t);
    protocol bridge for unknown number types.
    """
    ...

def num_inplace_matmul(o1: object, o2: object) -> object:
    """Return in-place ``o1 @= o2`` result via ``PyNumber_InPlaceMatrixMultiply``.

    Notes
    -----
    Mixed Tier A parity: 0.90x (3.14), 1.08x (3.14t), 1.00x (3.15), 1.00x (3.15t);
    protocol bridge for unknown number types.
    """
    ...

def num_inplace_floordiv(o1: object, o2: object) -> object:
    """Return in-place ``o1 //= o2`` result via ``PyNumber_InPlaceFloorDivide``.

    Notes
    -----
    Mixed Tier A parity: 1.02x (3.14), 1.00x (3.14t), 1.02x (3.15), 0.99x (3.15t);
    protocol bridge for unknown number types.
    """
    ...

def num_inplace_truediv(o1: object, o2: object) -> object:
    """Return in-place ``o1 /= o2`` result via ``PyNumber_InPlaceTrueDivide``.

    Notes
    -----
    Mixed Tier A parity: 1.02x (3.14), 1.02x (3.14t), 0.99x (3.15), 0.98x (3.15t);
    protocol bridge for unknown number types.
    """
    ...

def num_inplace_mod(o1: object, o2: object) -> object:
    """Return in-place ``o1 %= o2`` result via ``PyNumber_InPlaceRemainder``.

    Notes
    -----
    Mixed Tier A parity: 0.97x (3.14), 1.22x (3.14t), 0.99x (3.15), 0.98x (3.15t);
    protocol bridge for unknown number types.
    """
    ...

def num_inplace_pow(o1: object, o2: object, o3: object = None) -> object:
    """Return in-place power via ``PyNumber_InPlacePower``."""
    ...

def num_inplace_lshift(o1: object, o2: object) -> object:
    """Return in-place ``o1 <<= o2`` result via ``PyNumber_InPlaceLshift``.

    Notes
    -----
    Mixed Tier A parity: 1.01x (3.14), 1.02x (3.14t), 1.05x (3.15), 1.00x (3.15t);
    protocol bridge for unknown number types.
    """
    ...

def num_inplace_rshift(o1: object, o2: object) -> object:
    """Return in-place ``o1 >>= o2`` result via ``PyNumber_InPlaceRshift``."""
    ...

def num_inplace_and(o1: object, o2: object) -> object:
    """Return in-place ``o1 &= o2`` result via ``PyNumber_InPlaceAnd``."""
    ...

def num_inplace_xor(o1: object, o2: object) -> object:
    """Return in-place ``o1 ^= o2`` result via ``PyNumber_InPlaceXor``."""
    ...

def num_inplace_or(o1: object, o2: object) -> object:
    """Return in-place ``o1 |= o2`` result via ``PyNumber_InPlaceOr``.

    Notes
    -----
    Mixed Tier A parity: 1.01x (3.14), 1.02x (3.14t), 1.01x (3.15), 0.99x (3.15t);
    protocol bridge for unknown number types.
    """
    ...

def num_float(o: object) -> object:
    """Return ``float(o)`` via ``PyNumber_Float``.

    Notes
    -----
    Slower than the plain-Python equivalent ``float(x)`` (Tier A 1.03–1.06x);
    protocol bridge for unknown number types.
    """
    ...

def num_abs(o: object) -> object:
    """Return ``abs(o)`` via ``PyNumber_Absolute``."""
    ...

def num_add(o1: object, o2: object) -> object:
    """Return ``o1 + o2`` via ``PyNumber_Add``.

    Notes
    -----
    Mixed Tier A parity: 0.99x (3.14), 1.06x (3.14t), 1.00x (3.15), 1.03x (3.15t);
    protocol bridge for unknown number types.
    """
    ...

def num_and(o1: object, o2: object) -> object:
    """Return ``o1 & o2`` via ``PyNumber_And``.

    Notes
    -----
    Mixed Tier A parity: 0.95x (3.14), 1.03x (3.14t), 0.99x (3.15), 0.97x (3.15t);
    protocol bridge for unknown number types.
    """
    ...

def num_as_ssize(o: object, exc: object | None = None) -> int:
    """Return the ``Py_ssize_t`` of ``o`` (``PyNumber_AsSsize_t``), raising ``exc`` on overflow.

    Notes
    -----
    Slower than the plain-Python equivalent ``operator.index(x)`` (Tier A
    1.03–1.13x); protocol bridge for unknown number types.
    """
    ...

def num_index(o: object) -> object:
    """Return the index integer of ``o`` (``PyNumber_Index``)."""
    ...

def num_long(o: object) -> object:
    """Return ``int(o)`` via ``PyNumber_Long``.

    Notes
    -----
    Slower than the plain-Python equivalent ``int(x)`` (Tier A 1.04–1.09x); protocol
    bridge for unknown number types.
    """
    ...

def num_mod(o1: object, o2: object) -> object:
    """Return ``o1 % o2`` via ``PyNumber_Mod``.

    Notes
    -----
    Mixed Tier A parity: 0.97x (3.14), 1.08x (3.14t), 1.00x (3.15), 0.98x (3.15t);
    protocol bridge for unknown number types.
    """
    ...

def num_mul(o1: object, o2: object) -> object:
    """Return ``o1 * o2`` via ``PyNumber_Multiply``.

    Notes
    -----
    Mixed Tier A parity: 0.95x (3.14), 1.07x (3.14t), 1.00x (3.15), 0.99x (3.15t);
    protocol bridge for unknown number types.
    """
    ...

def num_neg(o: object) -> object:
    """Return ``-o`` via ``PyNumber_Negative``."""
    ...

def num_pow(o1: object, o2: object, o3: object | None = None) -> object:
    """Return ``pow(o1, o2)`` (``PyNumber_Power``), with optional modulus ``o3``.

    Notes
    -----
    Mixed Tier A parity: 0.95x (3.14), 1.07x (3.14t), 1.00x (3.15), 1.00x (3.15t);
    protocol bridge for unknown number types.
    """
    ...

def num_truediv(o1: object, o2: object) -> object:
    """Return ``o1 / o2`` via ``PyNumber_TrueDivide``."""
    ...
