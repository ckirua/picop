"""Smoke for :mod:`picop.hot` (DX-01 curated starters).

Run: python examples/pyhot.py
"""

from picop.hot import (
    array_eq,
    array_ne,
    bytearray_contains,
    bytearray_eq,
    bytearray_ne,
    bytes_contains,
    bytes_eq,
    bytes_len,
    bytes_ne,
    bytes_endswith,
    bytes_startswith,
    dict_get,
    dict_len,
    list_append,
    list_len,
    memoryview_eq,
    memoryview_ne,
    set_add,
    set_contains,
    str_len,
    tuple_pack2,
)

def main() -> None:
    d = {"a": 1}
    assert dict_get(d, "a") == 1 and dict_len(d) == 1
    xs: list[object] = []
    assert list_append(xs, 7) == 0 and list_len(xs) == 1
    s: set[object] = set()
    set_add(s, "x")
    assert set_contains(s, "x")
    assert tuple_pack2(1, 2) == (1, 2)
    assert bytes_len(b"ok") == 2 and bytes_contains(b"ab", b"a")
    assert bytes_eq(b"ok", b"ok") and not bytes_eq(b"ok", b"no")
    assert bytes_ne(b"ok", b"no") and not bytes_ne(b"ok", b"ok")
    assert bytes_startswith(b"ok", b"o") and not bytes_startswith(b"ok", b"x")
    assert bytes_endswith(b"ok", b"k") and not bytes_endswith(b"ok", b"x")
    assert bytearray_eq(bytearray(b"ok"), bytearray(b"ok"))
    assert bytearray_ne(bytearray(b"ok"), bytearray(b"no"))
    assert bytearray_contains(bytearray(b"ok"), b"o")
    from array import array as Array
    assert array_eq(Array("i", [1, 2]), Array("i", [1, 2]))
    assert array_ne(Array("i", [1, 2]), Array("i", [1, 3]))
    assert memoryview_eq(memoryview(b"ok"), memoryview(b"ok"))
    assert memoryview_ne(memoryview(b"ok"), memoryview(b"no"))
    assert str_len("hi") == 2
    print("ok", dict_len(d), list_len(xs), bytes_len(b"ok"))

if __name__ == "__main__":
    main()
