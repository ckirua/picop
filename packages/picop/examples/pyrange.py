"""Python usage for picop cyrange.

Run: python examples/pyrange.py
"""
from picop import range_eq


def main() -> None:
    assert range_eq(range(5), range(5))
    assert range_eq(range(0, 10, 3), range(0, 11, 3))  # same sequence
    assert range_eq(range(0), range(1, 1))  # empty
    assert range_eq(range(0, 10, -1), range(0, 10, -1))
    assert not range_eq(range(5), range(6))
    assert not range_eq(range(0, 10, 2), range(0, 10, 3))
    a = range(1, 8, 2)
    assert range_eq(a, a)
    assert range_eq(a, range(1, 8, 2)) == (a == range(1, 8, 2))
    print("ok", list(a))


if __name__ == "__main__":
    main()
