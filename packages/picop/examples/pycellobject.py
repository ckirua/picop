"""Python usage for picop cycellobject.

Run: python examples/pycellobject.py
"""
import types

from picop import cell_check, cell_eq, cell_new, cell_get, cell_set


def main() -> None:
    c = cell_new(None)
    assert cell_check(c)
    assert cell_get(c) is None
    cell_set(c, 42)
    assert cell_get(c) == 42
    a = cell_new(1)
    b = cell_new(1)
    assert cell_eq(a, b) and not cell_eq(a, cell_new(2))
    assert cell_eq(a, a)
    e1, e2 = types.CellType(), types.CellType()
    assert cell_eq(e1, e2) and not cell_eq(e1, a)
    print("ok", cell_get(c))


if __name__ == "__main__":
    main()
