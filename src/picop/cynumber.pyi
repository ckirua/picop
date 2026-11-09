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
    Slower than the plain-Python equivalent ``a // b`` (Tier A 1.03x); protocol
    bridge for unknown number types.
    """
    ...

def num_sub(o1: object, o2: object) -> object:
    """Return ``o1 - o2`` via ``PyNumber_Subtract``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a - b`` (Tier A 1.09x); protocol
    bridge for unknown number types.
    """
    ...

def num_matmul(o1: object, o2: object) -> object:
    """Return ``o1 @ o2`` via ``PyNumber_MatrixMultiply``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a @ b`` (Tier A 1.09x); protocol
    bridge for unknown number types.
    """
    ...

def num_divmod(o1: object, o2: object) -> object:
    """Return ``divmod(o1, o2)`` via ``PyNumber_Divmod``.

    Notes
    -----
    Slower than the plain-Python equivalent ``divmod(a, b)`` (Tier A 1.06x);
    protocol bridge for unknown number types.
    """
    ...

def num_pos(o: object) -> object:
    """Return ``+o`` via ``PyNumber_Positive``.

    Notes
    -----
    Slower than the plain-Python equivalent ``+a`` (Tier A 1.09x); protocol bridge
    for unknown number types.
    """
    ...

def num_invert(o: object) -> object:
    """Return ``~o`` via ``PyNumber_Invert``.

    Notes
    -----
    Slower than the plain-Python equivalent ``~a`` (Tier A 1.08x); protocol bridge
    for unknown number types.
    """
    ...

def num_lshift(o1: object, o2: object) -> object:
    """Return ``o1 << o2`` via ``PyNumber_Lshift``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a << b`` (Tier A 1.06x); protocol
    bridge for unknown number types.
    """
    ...

def num_rshift(o1: object, o2: object) -> object:
    """Return ``o1 >> o2`` via ``PyNumber_Rshift``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a >> b`` (Tier A 1.07x); protocol
    bridge for unknown number types.
    """
    ...

def num_xor(o1: object, o2: object) -> object:
    """Return ``o1 ^ o2`` via ``PyNumber_Xor``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a ^ b`` (Tier A 1.08x); protocol
    bridge for unknown number types.
    """
    ...

def num_or(o1: object, o2: object) -> object:
    """Return ``o1 | o2`` via ``PyNumber_Or``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a | b`` (Tier A 1.07x); protocol
    bridge for unknown number types.
    """
    ...

def num_inplace_add(o1: object, o2: object) -> object:
    """Return in-place ``o1 += o2`` result via ``PyNumber_InPlaceAdd``."""
    ...

def num_inplace_sub(o1: object, o2: object) -> object:
    """Return in-place ``o1 -= o2`` result via ``PyNumber_InPlaceSubtract``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a -= b`` (Tier A 1.04x); protocol
    bridge for unknown number types.
    """
    ...

def num_inplace_mul(o1: object, o2: object) -> object:
    """Return in-place ``o1 *= o2`` result via ``PyNumber_InPlaceMultiply``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a *= b`` (Tier A 1.04x); protocol
    bridge for unknown number types.
    """
    ...

def num_inplace_matmul(o1: object, o2: object) -> object:
    """Return in-place ``o1 @= o2`` result via ``PyNumber_InPlaceMatrixMultiply``."""
    ...

def num_inplace_floordiv(o1: object, o2: object) -> object:
    """Return in-place ``o1 //= o2`` result via ``PyNumber_InPlaceFloorDivide``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a //= b`` (Tier A 1.03x); protocol
    bridge for unknown number types.
    """
    ...

def num_inplace_truediv(o1: object, o2: object) -> object:
    """Return in-place ``o1 /= o2`` result via ``PyNumber_InPlaceTrueDivide``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a /= b`` (Tier A 1.06x); protocol
    bridge for unknown number types.
    """
    ...

def num_inplace_mod(o1: object, o2: object) -> object:
    """Return in-place ``o1 %= o2`` result via ``PyNumber_InPlaceRemainder``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a %= b`` (Tier A 1.04x); protocol
    bridge for unknown number types.
    """
    ...

def num_inplace_pow(o1: object, o2: object, o3: object = None) -> object:
    """Return in-place power via ``PyNumber_InPlacePower``."""
    ...

def num_inplace_lshift(o1: object, o2: object) -> object:
    """Return in-place ``o1 <<= o2`` result via ``PyNumber_InPlaceLshift``."""
    ...

def num_inplace_rshift(o1: object, o2: object) -> object:
    """Return in-place ``o1 >>= o2`` result via ``PyNumber_InPlaceRshift``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a >>= b`` (Tier A 1.04x); protocol
    bridge for unknown number types.
    """
    ...

def num_inplace_and(o1: object, o2: object) -> object:
    """Return in-place ``o1 &= o2`` result via ``PyNumber_InPlaceAnd``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a &= b`` (Tier A 1.05x); protocol
    bridge for unknown number types.
    """
    ...

def num_inplace_xor(o1: object, o2: object) -> object:
    """Return in-place ``o1 ^= o2`` result via ``PyNumber_InPlaceXor``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a ^= b`` (Tier A 1.07x); protocol
    bridge for unknown number types.
    """
    ...

def num_inplace_or(o1: object, o2: object) -> object:
    """Return in-place ``o1 |= o2`` result via ``PyNumber_InPlaceOr``."""
    ...

def num_float(o: object) -> object:
    """Return ``float(o)`` via ``PyNumber_Float``.

    Notes
    -----
    Slower than the plain-Python equivalent ``float(x)`` (Tier A 1.03x); protocol
    bridge for unknown number types.
    """
    ...

def num_abs(o: object) -> object:
    """Return ``abs(o)`` via ``PyNumber_Absolute``."""
    ...

def num_add(o1: object, o2: object) -> object:
    """Return ``o1 + o2`` via ``PyNumber_Add``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a + b`` (Tier A 1.30x); protocol
    bridge for unknown number types.
    """
    ...

def num_and(o1: object, o2: object) -> object:
    """Return ``o1 & o2`` via ``PyNumber_And``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a & b`` (Tier A 1.06x); protocol
    bridge for unknown number types.
    """
    ...

def num_as_ssize(o: object, exc: object | None = None) -> int:
    """Return the ``Py_ssize_t`` of ``o`` (``PyNumber_AsSsize_t``), raising ``exc`` on overflow."""
    ...

def num_index(o: object) -> object:
    """Return the index integer of ``o`` (``PyNumber_Index``).

    Notes
    -----
    Slower than the plain-Python equivalent ``operator.index(x)`` (Tier A 1.19x);
    protocol bridge for unknown number types.
    """
    ...

def num_long(o: object) -> object:
    """Return ``int(o)`` via ``PyNumber_Long``.

    Notes
    -----
    Slower than the plain-Python equivalent ``int(x)`` (Tier A 1.17x); protocol
    bridge for unknown number types.
    """
    ...

def num_mod(o1: object, o2: object) -> object:
    """Return ``o1 % o2`` via ``PyNumber_Mod``."""
    ...

def num_mul(o1: object, o2: object) -> object:
    """Return ``o1 * o2`` via ``PyNumber_Multiply``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a * b`` (Tier A 1.19x); protocol
    bridge for unknown number types.
    """
    ...

def num_neg(o: object) -> object:
    """Return ``-o`` via ``PyNumber_Negative``."""
    ...

def num_pow(o1: object, o2: object, o3: object | None = None) -> object:
    """Return ``pow(o1, o2)`` (``PyNumber_Power``), with optional modulus ``o3``.

    Notes
    -----
    Slower than the plain-Python equivalent ``pow(a, b)`` (Tier A 1.24x); protocol
    bridge for unknown number types.
    """
    ...

def num_truediv(o1: object, o2: object) -> object:
    """Return ``o1 / o2`` via ``PyNumber_TrueDivide``.

    Notes
    -----
    Slower than the plain-Python equivalent ``a / b`` (Tier A 1.13x); protocol
    bridge for unknown number types.
    """
    ...
