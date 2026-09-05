"""Python usage for picop cyfunction.

Run: python examples/pyfunction.py
"""
from picop import func_check, func_eq, func_get_code, func_get_globals


def main() -> None:
    def f(x):
        return x

    def g(x):
        return x

    assert func_check(f)
    assert func_get_code(f) is f.__code__
    assert func_get_globals(f) is f.__globals__
    assert func_eq(f, f) and not func_eq(f, g)
    assert func_eq(f, f) is (f is f)
    print("ok", func_check(f), func_eq(f, f))


if __name__ == "__main__":
    main()
