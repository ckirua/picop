"""Python usage of :func:`picop` set helpers.

Run: python examples/pyset.py
"""

from picop import (
    frozenset_eq,
    set_add,
    set_clear,
    set_contains,
    set_copy,
    set_discard,
    set_eq,
    set_len,
    set_pop,
    set_update,
)

SYMBOLS: set[str] = {"BTCUSDT", "ETHUSDT", "SOLUSDT"}

def main() -> None:
    assert set_eq({"a", "b"}, {"b", "a"}) and not set_eq({"a"}, {"b"}) and set_eq(set(), set())
    assert set_eq({1, 2, 3}, {3, 2, 1}) and not set_eq({1}, {1, 2})
    assert (
        frozenset_eq(frozenset({"a", "b"}), frozenset({"b", "a"}))
        and not frozenset_eq(frozenset({"a"}), frozenset({"b"}))
        and frozenset_eq(frozenset(), frozenset())
    )
    assert frozenset_eq(frozenset({1, 2, 3}), frozenset({3, 2, 1})) and not frozenset_eq(
        frozenset({1}), frozenset({1, 2})
    )
    print(f"set_len(symbols) -> {set_len(SYMBOLS)!r}")
    for symbol in sorted(SYMBOLS):
        print(f"set_contains(symbols, {symbol!r}) -> {set_contains(SYMBOLS, symbol)!r}")

    working = set(SYMBOLS)
    rc = set_add(working, "BNBUSDT")
    print(f"set_add(symbols, 'BNBUSDT') -> rc={rc!r}, set={sorted(working)!r}")

    working = set(SYMBOLS)
    rc = set_discard(working, "ETHUSDT")
    print(f"set_discard(symbols, 'ETHUSDT') -> rc={rc!r}, set={sorted(working)!r}")

    working = set(SYMBOLS)
    rc = set_discard(working, "XRPUSDT")
    print(f"set_discard(symbols, 'XRPUSDT') -> rc={rc!r}, set={sorted(working)!r}")

    working = set(SYMBOLS)
    rc = set_update(working, {"ADAUSDT", "XRPUSDT"})
    print(f"set_update(symbols, ...) -> rc={rc!r}, set={sorted(working)!r}")

    copied = set_copy(SYMBOLS)
    print(f"set_copy(symbols) -> {sorted(copied)!r}")

    working = set(SYMBOLS)
    popped = set_pop(working)
    print(f"set_pop(symbols) -> {popped!r}, set={sorted(working)!r}")

    working = set(SYMBOLS)
    rc = set_clear(working)
    print(f"set_clear(symbols) -> rc={rc!r}, set={sorted(working)!r}")

    assert set_len(SYMBOLS) == len(SYMBOLS)
    assert set_contains(SYMBOLS, "BTCUSDT") is True
    assert set_contains(SYMBOLS, "XRPUSDT") is False
    assert set_copy(SYMBOLS) == SYMBOLS
    assert set_copy(SYMBOLS) is not SYMBOLS

    add_working: set[str] = set()
    assert set_add(add_working, "BTCUSDT") == 0
    assert add_working == {"BTCUSDT"}

    discard_working = set(SYMBOLS)
    assert set_discard(discard_working, "ETHUSDT") == 1
    assert set_discard(discard_working, "ETHUSDT") == 0

    update_working = {"BTCUSDT"}
    assert set_update(update_working, ["ETHUSDT", "SOLUSDT"]) == 0
    assert update_working == {"BTCUSDT", "ETHUSDT", "SOLUSDT"}

    clear_working = set(SYMBOLS)
    assert set_clear(clear_working) == 0
    assert clear_working == set()

    print("assertions passed")

if __name__ == "__main__":
    main()
