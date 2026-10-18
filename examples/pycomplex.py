"""Python usage for picop cycomplex.

Run: python examples/pycomplex.py
"""
from picop import (
    complex_check,
    complex_eq,
    complex_from_doubles,
    complex_imag_as_double,
    complex_real_as_double,
)


def main() -> None:
    z = complex_from_doubles(1.5, -2.0)
    assert complex_check(z)
    assert complex_real_as_double(z) == 1.5
    assert complex_imag_as_double(z) == -2.0
    assert complex_eq(z, 1.5 - 2.0j) and not complex_eq(z, 1.5 + 2.0j)
    assert complex_eq(0j, -0.0j) and complex_eq(-0.0 + 0j, 0j)
    nan = float("nan")
    zn = complex(nan, 0.0)
    assert not complex_eq(zn, zn) and not (zn == zn)
    assert complex_eq(1 + 0j, 1) and complex_eq(1 + 0j, 1.0)
    print("ok", z)


if __name__ == "__main__":
    main()
