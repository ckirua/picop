"""Python usage for picop cyfunction.

Run: python examples/pyfunction.py
"""
from picop import (
    func_check,
    func_eq,
    func_get_annotations,
    func_get_code,
    func_get_globals,
    func_get_kw_defaults,
    func_new_with_qualname,
    func_set_annotations,
    func_set_kw_defaults,
)


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

    # kw-defaults and annotations are the C-level fields, not attribute lookups
    def h(x, *, y=1):
        return x + y

    assert func_set_kw_defaults(h, {"y": 3}) == 0
    assert h(3, y=5) == 8
    assert func_get_kw_defaults(h) == {"y": 3}
    func_set_annotations(h, {"x": int, "y": int})
    assert func_get_annotations(h) == {"x": int, "y": int}

    wrapped = func_new_with_qualname(h.__code__, h.__globals__, "module.h")
    assert wrapped.__qualname__ == "module.h"
    assert wrapped(2, y=1) == 3

    print("ok", func_check(f), func_eq(f, f))


if __name__ == "__main__":
    main()
