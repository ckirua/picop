"""Python usage of :func:`picop` str helpers.

Run: python examples/pystr.py
"""

from picop import (
    str_all_alnum_ascii,
    str_all_digits,
    str_as_or_empty,
    str_cmp,
    str_contains,
    str_ge,
    str_gt,
    str_le,
    str_lt,
    str_eq,
    str_is,
    str_is_blank,
    str_len,
    str_none_to_empty,
    str_or_empty,
    str_startswith,
)

SYMBOL: str = "BTCUSDT"
HAYSTACK: str = "abcabc"

# Which coerce helper? (usually skip on hot paths — not in picop.hot)
# - str_or_empty: truthy exact str → self; else ""
# - str_as_or_empty: exact str → self; else "" (keeps empty str)
# - str_none_to_empty: exact str → self; else "" (incl. None)
# - str_or_none: exact str → self; else None
# - str_is / str_is_not: type gates, not coerce
# Hot typed str: prefer str_len / str_eq / str_contains

STR_OR_EMPTY_CASES: tuple[tuple[object, str], ...] = (
    ("BTCUSDT", "BTCUSDT"),
    ("", ""),
    (None, ""),
    (123, ""),
)

AS_STR_OR_EMPTY_CASES: tuple[tuple[object, str], ...] = (
    ("BTCUSDT", "BTCUSDT"),
    ("", ""),
    (None, ""),
    (123, ""),
)

NONE_TO_EMPTY_CASES: tuple[tuple[object, str], ...] = (
    ("BTCUSDT", "BTCUSDT"),
    ("", ""),
    (None, ""),
    (123, ""),
)

CONTAINS_CASES: tuple[tuple[str, str, bool], ...] = (
    (HAYSTACK, "b", True),
    (HAYSTACK, "z", False),
    (HAYSTACK, "ab", True),
    (HAYSTACK, "xy", False),
    (SYMBOL, "USDT", True),
    (SYMBOL, "ETH", False),
)

def main() -> None:
    assert str_cmp("a", "b") < 0 and str_cmp("b", "a") > 0 and str_cmp("x", "x") == 0
    assert str_lt("a", "b") and str_le("a", "a") and str_gt("b", "a") and str_ge("b", "b")
    print(f"str_len({SYMBOL!r}) -> {str_len(SYMBOL)!r}")
    assert str_len(SYMBOL) == len(SYMBOL)
    assert str_len("") == 0

    print(f"str_eq({SYMBOL!r}, {SYMBOL!r}) -> {str_eq(SYMBOL, SYMBOL)!r}")
    assert str_eq(SYMBOL, SYMBOL) is True
    assert str_eq(SYMBOL, "ETHUSDT") is False

    print(f"str_startswith({SYMBOL!r}, 'BTC') -> {str_startswith(SYMBOL, 'BTC')!r}")
    assert str_startswith(SYMBOL, "BTC") is True
    assert str_startswith(SYMBOL, "ETH") is False

    print()
    for value, expected in STR_OR_EMPTY_CASES:
        result = str_or_empty(value)
        status = "ok" if result == expected else "FAIL"
        print(f"{status:4}  str_or_empty({value!r:>12}) -> {result!r}")

    print()
    for value, expected in AS_STR_OR_EMPTY_CASES:
        result = str_as_or_empty(value)
        status = "ok" if result == expected else "FAIL"
        print(f"{status:4}  str_as_or_empty({value!r:>12}) -> {result!r}")

    print()
    for value, expected in NONE_TO_EMPTY_CASES:
        result = str_none_to_empty(value)
        status = "ok" if result == expected else "FAIL"
        print(f"{status:4}  str_none_to_empty({value!r:>12}) -> {result!r}")

    print()
    for haystack, needle, expected in CONTAINS_CASES:
        result = str_contains(haystack, needle)
        py_result = needle in haystack
        status = "ok" if result == expected == py_result else "FAIL"
        print(
            f"{status:4}  {needle!r:>6} in {haystack!r:>10}  "
            f"-> {result!r}  (python {py_result!r})"
        )

    print()
    print(f"str_all_digits('12345') -> {str_all_digits('12345')!r}")
    print(f"str_all_digits({SYMBOL!r}) -> {str_all_digits(SYMBOL)!r}")
    assert str_all_digits("12345") is True
    assert str_all_digits(SYMBOL) is False

    print(f"str_all_alnum_ascii({SYMBOL!r}) -> {str_all_alnum_ascii(SYMBOL)!r}")
    print(f"str_all_alnum_ascii('BTC-USDT') -> {str_all_alnum_ascii('BTC-USDT')!r}")
    assert str_all_alnum_ascii(SYMBOL) is True
    assert str_all_alnum_ascii("BTC-USDT") is False

    print(f"str_is_blank('   ') -> {str_is_blank('   ')!r}")
    print(f"str_is_blank({SYMBOL!r}) -> {str_is_blank(SYMBOL)!r}")
    assert str_is_blank("   ") is True
    assert str_is_blank(SYMBOL) is False

    print(f"str_is({SYMBOL!r}) -> {str_is(SYMBOL)!r}")
    print(f"str_is(123) -> {str_is(123)!r}")
    assert str_is(SYMBOL) is True
    assert str_is(123) is False

    print()
    print("assertions passed")

if __name__ == "__main__":
    main()
