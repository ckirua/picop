"""Python usage of :func:`picop.bytes_len`, :func:`picop.bytes_contains`, :func:`picop.bytes_eq`, :func:`picop.bytes_ne`, :func:`picop.bytes_startswith`, :func:`picop.bytes_endswith`.

Run: python examples/pybytes.py
"""

from picop import (
    bytes_bytearray_eq,
    bytes_contains,
    bytes_eq,
    bytes_endswith,
    bytes_len,
    bytes_ne,
    bytes_startswith,
)
PAYLOAD: bytes = b"BTCUSDT"
HAYSTACK: bytes = b"abcabc"

BCONTAINS_CASES: tuple[tuple[bytes, bytes, bool], ...] = (
    (HAYSTACK, b"b", True),   # single-byte hit  (memchr)
    (HAYSTACK, b"z", False),  # single-byte miss
    (HAYSTACK, b"ab", True),  # multi-byte hit   (memmem)
    (HAYSTACK, b"xy", False), # multi-byte miss
    (HAYSTACK, b"", True),    # empty needle
    (b"", b"a", False),       # empty haystack
)

BEQ_CASES: tuple[tuple[bytes, bytes, bool], ...] = (
    (PAYLOAD, PAYLOAD, True),       # identity
    (PAYLOAD, b"BTCUSDT", True),    # equal content
    (PAYLOAD, b"ETHUSDT", False),   # same len, different
    (PAYLOAD, b"BTC", False),       # different len
    (b"", b"", True),               # empty
)

BSTARTSWITH_CASES: tuple[tuple[bytes, bytes, bool], ...] = (
    (PAYLOAD, b"BTC", True),
    (PAYLOAD, b"ETH", False),
    (PAYLOAD, b"", True),
    (PAYLOAD, b"BTCUSDTX", False),
    (b"", b"", True),
)

BENDSWITH_CASES: tuple[tuple[bytes, bytes, bool], ...] = (
    (PAYLOAD, b"USDT", True),
    (PAYLOAD, b"BTC", False),
    (PAYLOAD, b"", True),
    (PAYLOAD, b"XBTCUSDT", False),
    (b"", b"", True),
)

def main() -> None:
    print(f"bytes_len(payload) -> {bytes_len(PAYLOAD)!r}")
    assert bytes_len(PAYLOAD) == len(PAYLOAD)
    assert bytes_len(b"") == 0

    print()
    for haystack, needle, expected in BCONTAINS_CASES:
        result = bytes_contains(haystack, needle)
        py_result = needle in haystack
        status = "ok" if result == expected == py_result else "FAIL"
        print(
            f"{status:4}  {needle!r:>6} in {haystack!r:>10}  "
            f"-> {result!r}  (python {py_result!r})"
        )
        assert result == expected
        assert result == py_result

    print()
    for a, b, expected in BEQ_CASES:
        result = bytes_eq(a, b)
        py_result = a == b
        status = "ok" if result == expected == py_result else "FAIL"
        print(
            f"{status:4}  bytes_eq({a!r}, {b!r})  "
            f"-> {result!r}  (python {py_result!r})"
        )
        assert result == expected
        assert result == py_result
        assert bytes_ne(a, b) == (not expected) == (a != b)

    print()
    for s, prefix, expected in BSTARTSWITH_CASES:
        result = bytes_startswith(s, prefix)
        py_result = s.startswith(prefix)
        status = "ok" if result == expected == py_result else "FAIL"
        print(
            f"{status:4}  bytes_startswith({s!r}, {prefix!r})  "
            f"-> {result!r}  (python {py_result!r})"
        )
        assert result == expected
        assert result == py_result

    print()
    for s, suffix, expected in BENDSWITH_CASES:
        result = bytes_endswith(s, suffix)
        py_result = s.endswith(suffix)
        status = "ok" if result == expected == py_result else "FAIL"
        print(
            f"{status:4}  bytes_endswith({s!r}, {suffix!r})  "
            f"-> {result!r}  (python {py_result!r})"
        )
        assert result == expected
        assert result == py_result

    print()
    # Cross-type bytes ↔ bytearray (issue #43)
    ba = bytearray(PAYLOAD)
    assert bytes_bytearray_eq(PAYLOAD, ba)
    assert bytes_bytearray_eq(ba, PAYLOAD)
    assert bytes_bytearray_eq(PAYLOAD, PAYLOAD)
    assert bytes_bytearray_eq(ba, bytearray(PAYLOAD))
    assert not bytes_bytearray_eq(PAYLOAD, bytearray(b"ETHUSDT"))
    assert bytes_bytearray_eq(b"", bytearray())
    assert bytes_bytearray_eq(PAYLOAD, ba) == (PAYLOAD == ba)
    print("ok    bytes_bytearray_eq both directions")

    print()
    print("assertions passed")

if __name__ == "__main__":
    main()
