"""Python usage for picop cylong.

Run: python examples/pylong.py
"""
from picop import int_eq, long_check, long_eq, long_from_long, long_from_ssize


def main() -> None:
    n = long_from_long(99)
    assert long_check(n) and n == 99
    assert long_from_ssize(7) == 7
    assert long_eq(1, 1) and not long_eq(1, 2) and long_eq(0, 0)
    assert int_eq(99, n) and long_eq(10**100, 10**100) and not long_eq(10**100, 10**100 + 1)
    print("ok", n)


if __name__ == "__main__":
    main()
