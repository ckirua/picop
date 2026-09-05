"""Python usage for picop cynumber.

Run: python examples/pynumber.py
"""
from picop import num_check, num_eq, num_floordiv, num_inplace_add
from picop import protocols


def main() -> None:
    assert num_check(3)
    assert num_floordiv(7, 2) == 3
    assert num_inplace_add(10, 3) == 13
    assert num_eq(1, 1) and not num_eq(1, 2) and num_eq(0, 0)
    assert num_eq(1.5, 1.5) and num_eq(0.0, -0.0) and num_eq(1, 1.0)
    assert num_eq(1 + 0j, 1) and not num_eq(1j, 2j)
    nan = float("nan")
    assert not num_eq(nan, nan) and not (nan == nan)
    assert protocols.num_eq(10, 10) and not protocols.num_eq(10, 11)
    print("ok", num_floordiv(5, 2))


if __name__ == "__main__":
    main()
