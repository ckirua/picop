"""Python usage for picop cyiterator.

Run: python examples/pyiterator.py
"""
from picop import iter_check, iter_eq, iter_next


def main() -> None:
    it = iter([10, 20])
    other = iter([10, 20])
    assert iter_check(it)
    assert iter_eq(it, it) and not iter_eq(it, other)
    assert iter_eq(it, it) is (it is it)
    assert iter_next(it) == 10
    assert iter_next(it) == 20
    print("ok", iter_check(it), iter_eq(it, it))


if __name__ == "__main__":
    main()
