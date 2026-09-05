"""Python usage for picop cyweakref.

Run: python examples/pyweakref.py
"""
from picop import weakref_check, weakref_eq, weakref_new_ref


def main() -> None:
    class T:
        pass

    obj = T()
    other = T()
    a = weakref_new_ref(obj, lambda r: None)
    b = weakref_new_ref(obj, lambda r: None)
    c = weakref_new_ref(other, lambda r: None)
    assert weakref_check(a)
    assert a() is obj
    assert weakref_eq(a, b) and not weakref_eq(a, c)
    assert weakref_eq(a, a)
    assert weakref_eq(a, b) is (a == b)
    print("ok", weakref_check(a), weakref_eq(a, b))


if __name__ == "__main__":
    main()
