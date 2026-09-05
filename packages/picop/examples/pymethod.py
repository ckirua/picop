"""Python usage for picop cymethod.

Run: python examples/pymethod.py
"""
from picop import (
    method_check,
    method_eq,
    method_new,
    method_get_function,
    method_get_self,
)


def main() -> None:
    def f(self):
        return 1

    class C:
        pass

    c = C()
    m = method_new(f, c)
    m2 = method_new(f, c)
    m3 = method_new(f, C())
    assert method_check(m)
    assert method_get_function(m) is f
    assert isinstance(method_get_self(m), C)
    assert method_eq(m, m2) and not method_eq(m, m3)
    assert method_eq(m, m)
    assert method_eq(m, m2) is (m == m2)
    print("ok", method_check(m), method_eq(m, m2))


if __name__ == "__main__":
    main()
