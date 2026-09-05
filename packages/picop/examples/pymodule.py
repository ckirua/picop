"""Python usage for picop cymodule.

Run: python examples/pymodule.py
"""
import sys
from picop import mod_check, mod_eq, mod_get_name


def main() -> None:
    m = sys.modules["sys"]
    other = sys.modules["os"]
    assert mod_check(m)
    assert mod_get_name(m) == "sys"
    assert mod_eq(m, m) and not mod_eq(m, other)
    assert mod_eq(m, m) is (m is m)
    print("ok", mod_get_name(m), mod_eq(m, m))


if __name__ == "__main__":
    main()
