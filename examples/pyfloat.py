"""Python usage for picop cyfloat.

Run: python examples/pyfloat.py
"""
from picop import float_as_double, float_check, float_eq, float_from_double


def main() -> None:
    x = float_from_double(2.5)
    assert float_check(x) and float_as_double(x) == 2.5
    assert float_eq(2.5, 2.5) and not float_eq(2.5, 2.6)
    assert float_eq(0.0, -0.0) and float_eq(-0.0, 0.0)
    nan = float("nan")
    assert not float_eq(nan, nan) and not (nan == nan)
    assert float_eq(1.0, 1)
    print("ok", x)


if __name__ == "__main__":
    main()
