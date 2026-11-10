"""Python usage for picop cymethod.

Run: python examples/pymethod.py
"""
from picop import (
    cfunction_check,
    cfunction_check_exact,
    cfunction_get_self,
    cmethod_check,
    cmethod_check_exact,
    classmethod_new,
    method_check,
    method_eq,
    method_get_function,
    method_get_self,
    method_new,
    staticmethod_new,
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

    # C functions: PyCMethod is a subtype of PyCFunction, so the exact variant
    # is the one that rejects it.
    assert cfunction_check(len) and cfunction_check_exact(len)
    assert not cfunction_check(f)
    assert cfunction_get_self(len) is len.__self__  # plain builtins carry builtins as m_self
    assert cfunction_get_self([].append) == []
    assert not cmethod_check(len)

    bound_cm = classmethod_new(f)
    bound_st = staticmethod_new(f)
    assert isinstance(bound_cm, classmethod) and isinstance(bound_st, staticmethod)
    assert C.__dict__.get("cm") is None
    C.cm = bound_cm
    C.st = bound_st
    assert C.cm() == 1 and C().st(1) == 1

    print("ok", method_check(m), method_eq(m, m2))


if __name__ == "__main__":
    main()
