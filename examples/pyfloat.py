"""Python usage for picop cyfloat.

Run: python examples/pyfloat.py
"""
import math
import struct
from picop.cyfloat import (
    float_as_double, float_check, float_eq, float_from_double,
    float_pack8, float_pack4, float_pack2,
    float_unpack8, float_unpack4, float_unpack2,
)

def main() -> None:
    x = float_from_double(2.5)
    assert float_check(x) and float_as_double(x) == 2.5
    assert float_eq(2.5, 2.5) and not float_eq(2.5, 2.6)
    assert float_eq(0.0, -0.0) and float_eq(-0.0, 0.0)
    nan = float("nan")
    assert not float_eq(nan, nan) and not (nan == nan)
    assert float_eq(1.0, 1)
    for pack, unpack, size in (
        (float_pack8, float_unpack8, 8),
        (float_pack4, float_unpack4, 4),
        (float_pack2, float_unpack2, 2),
    ):
        raw = pack(0.1)
        assert len(raw) == size and unpack(raw) == struct.unpack("<" + {8: "d", 4: "f", 2: "e"}[size], raw)[0]
        assert unpack(raw + b"extra") == unpack(raw)
    assert float_unpack2(float_pack2(0.1)) == 0.0999755859375
    assert float_pack8(float("inf")) and math.isnan(float_unpack8(float_pack8(float("nan"))))
    try:
        float_unpack8(b"short")
    except ValueError:
        pass
    else:
        raise AssertionError("short buffer accepted")
    print("ok", x)


if __name__ == "__main__":
    main()
