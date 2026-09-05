"""Python usage for picop cytype.

Run: python examples/pytype.py
"""
from picop import type_check, type_check_exact, type_eq, type_is_subtype


def main() -> None:
    assert type_check(int) and type_check_exact(int)
    assert type_is_subtype(bool, int)
    assert type_eq(int, int) and not type_eq(int, str)
    assert type_eq(bool, bool) and not type_eq(bool, int)
    print("ok", type_is_subtype(bool, int))


if __name__ == "__main__":
    main()
