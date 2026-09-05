"""Python usage of :mod:`picop` tuple helpers.

Run: python examples/pytuple.py
"""

from picop import (
    tuple_check,
    tuple_eq,
    tuple_get,
    tuple_get_checked,
    tuple_len,
    tuple_pack2,
    tuple_slice,
)

ROW: tuple[str, str, str] = ("BTCUSDT", "TRADING", "SPOT")

def main() -> None:
    assert tuple_eq((1, 2), (1, 2)) and not tuple_eq((1,), (2,)) and tuple_eq((), ())
    print(f"tuple_len(row) -> {tuple_len(ROW)!r}")
    for i in range(tuple_len(ROW)):
        print(f"tuple_get(row, {i}) -> {tuple_get(ROW, i)!r}")
    print(f"tuple_get_checked(row, 1) -> {tuple_get_checked(ROW, 1)!r}")
    print(f"tuple_slice(row, 0, 2) -> {tuple_slice(ROW, 0, 2)!r}")
    print(f"tuple_pack2('a','b') -> {tuple_pack2('a', 'b')!r}")
    print(f"tuple_check(row) -> {tuple_check(ROW)!r}")

    assert tuple_len(ROW) == len(ROW)
    assert tuple_get(ROW, 0) == ROW[0]
    assert tuple_slice(ROW, 1, 3) == ROW[1:3]
    assert tuple_pack2(1, 2) == (1, 2)
    print("assertions passed")

if __name__ == "__main__":
    main()
