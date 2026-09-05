"""Python usage for picop cyobject.

Run: python examples/pyobject.py
"""
from picop import obj_eq, obj_richcompare_bool
from picop import protocols

EQ = 2  # Py_EQ


def main() -> None:
    xs = [1, 2, 3]
    assert obj_eq(xs, [1, 2, 3]) and not obj_eq(xs, [1, 2])
    assert obj_eq(xs, xs)
    assert obj_richcompare_bool(1, 1, EQ)
    assert not obj_richcompare_bool(1, 2, EQ)
    assert protocols.obj_eq("a", "a") and not protocols.obj_eq("a", "b")
    print("ok", obj_eq(xs, [1, 2, 3]))


if __name__ == "__main__":
    main()
