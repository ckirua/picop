"""Python usage of :func:`picop` list helpers.

Run: python examples/pylist.py
"""

from picop import (
    list_append,
    list_clear,
    list_copy,
    list_empty,
    list_eq,
    list_extend,
    list_get,
    list_insert,
    list_len,
)

SYMBOLS: list[str] = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

def main() -> None:
    empty = list_empty()
    assert list_eq([1, 2], [1, 2]) and not list_eq([1], [2]) and list_eq([], [])
    print(f"list_empty() -> {empty!r}")
    assert empty == []
    assert list_empty() is not empty

    print(f"list_len(symbols) -> {list_len(SYMBOLS)!r}")
    for i in range(list_len(SYMBOLS)):
        print(f"list_get(symbols, {i}) -> {list_get(SYMBOLS, i)!r}")

    working = list(SYMBOLS)
    rc = list_append(working, "BNBUSDT")
    # rc is 0 on success — do not use as bool (`if list_append(...):` is wrong)
    print(f"list_append(symbols, 'BNBUSDT') -> rc={rc!r}, list={working!r}")

    working = list(SYMBOLS)
    rc = list_insert(working, 1, "SOLUSDT")
    print(f"list_insert(symbols, 1, 'SOLUSDT') -> rc={rc!r}, list={working!r}")

    working = list(SYMBOLS)
    rc = list_extend(working, ("XRPUSDT", "ADAUSDT"))
    print(f"list_extend(symbols, ('XRPUSDT', 'ADAUSDT')) -> rc={rc!r}, list={working!r}")

    copied = list_copy(SYMBOLS)
    print(f"list_copy(symbols) -> {copied!r}")

    working = list(SYMBOLS)
    rc = list_clear(working)
    print(f"list_clear(symbols) -> rc={rc!r}, list={working!r}")

    assert list_len(SYMBOLS) == len(SYMBOLS)
    assert list_get(SYMBOLS, 0) == SYMBOLS[0]
    assert list_append([], "x") == 0
    assert list_copy(SYMBOLS) == SYMBOLS
    assert list_copy(SYMBOLS) is not SYMBOLS

    insert_working: list[str] = []
    assert list_insert(insert_working, 0, "BTCUSDT") == 0
    assert insert_working == ["BTCUSDT"]

    extend_working: list[str] = ["BTCUSDT"]
    assert list_extend(extend_working, ["ETHUSDT"]) == 0
    assert extend_working == ["BTCUSDT", "ETHUSDT"]

    clear_working = list(SYMBOLS)
    assert list_clear(clear_working) == 0
    assert clear_working == []

    print("assertions passed")

if __name__ == "__main__":
    main()
