"""Abstract number-protocol helpers via the CPython C-API.

Prefer builtins for binary/unary ops from Python; keep checks, ``num_eq``,
and measured wins here when the operand type is unknown. Tier A losers remain
``cpdef`` but are omitted from stubs. See :doc:`/user_guide/quickstart`.
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
    """Return ``o1 // o2`` via ``PyNumber_FloorDivide``."""
    ...

def num_sub(o1: object, o2: object) -> object:
    """Return ``o1 - o2`` via ``PyNumber_Subtract``."""
    ...

def num_matmul(o1: object, o2: object) -> object:
    """Return ``o1 @ o2`` via ``PyNumber_MatrixMultiply``."""
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
    """Return ``o1 << o2`` via ``PyNumber_Lshift``."""
    ...

def num_rshift(o1: object, o2: object) -> object:
    """Return ``o1 >> o2`` via ``PyNumber_Rshift``."""
    ...

def num_xor(o1: object, o2: object) -> object:
    """Return ``o1 ^ o2`` via ``PyNumber_Xor``."""
    ...

def num_or(o1: object, o2: object) -> object:
    """Return ``o1 | o2`` via ``PyNumber_Or``."""
    ...

def num_inplace_add(o1: object, o2: object) -> object:
    """Return in-place ``o1 += o2`` result via ``PyNumber_InPlaceAdd``."""
    ...

def num_inplace_sub(o1: object, o2: object) -> object:
    """Return in-place ``o1 -= o2`` result via ``PyNumber_InPlaceSubtract``."""
    ...

def num_inplace_mul(o1: object, o2: object) -> object:
    """Return in-place ``o1 *= o2`` result via ``PyNumber_InPlaceMultiply``."""
    ...

def num_inplace_matmul(o1: object, o2: object) -> object:
    """Return in-place ``o1 @= o2`` result via ``PyNumber_InPlaceMatrixMultiply``."""
    ...

def num_inplace_floordiv(o1: object, o2: object) -> object:
    """Return in-place ``o1 //= o2`` result via ``PyNumber_InPlaceFloorDivide``."""
    ...

def num_inplace_truediv(o1: object, o2: object) -> object:
    """Return in-place ``o1 /= o2`` result via ``PyNumber_InPlaceTrueDivide``."""
    ...

def num_inplace_mod(o1: object, o2: object) -> object:
    """Return in-place ``o1 %= o2`` result via ``PyNumber_InPlaceRemainder``."""
    ...

def num_inplace_pow(o1: object, o2: object, o3: object = None) -> object:
    """Return in-place power via ``PyNumber_InPlacePower``."""
    ...

def num_inplace_lshift(o1: object, o2: object) -> object:
    """Return in-place ``o1 <<= o2`` result via ``PyNumber_InPlaceLshift``."""
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
    """Return in-place ``o1 |= o2`` result via ``PyNumber_InPlaceOr``."""
    ...

def num_float(o: object) -> object:
    """Return ``float(o)`` via ``PyNumber_Float``."""
    ...
