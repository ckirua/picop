"""Python usage for picop cybytearray.

Run: python examples/pybytearray.py
"""
from picop import (
    bytearray_check,
    bytearray_contains,
    bytearray_eq,
    bytearray_from_object,
    bytearray_len,
    bytearray_ne,
)


def main() -> None:
    ba = bytearray(b"hi")
    assert bytearray_check(ba) and bytearray_len(ba) == 2
    again = bytearray_from_object(b"xy")
    assert isinstance(again, bytearray) and bytes(again) == b"xy"
    assert bytearray_eq(ba, bytearray(b"hi")) and not bytearray_eq(ba, again)
    assert bytearray_eq(ba, ba)
    assert bytearray_ne(ba, again) and not bytearray_ne(ba, bytearray(b"hi"))
    assert bytearray_contains(ba, b"h") and not bytearray_contains(ba, b"x")
    assert bytearray_contains(ba, b"") and bytearray_contains(bytearray(b"abc"), b"bc")
    print("ok", bytearray_len(ba))


if __name__ == "__main__":
    main()
