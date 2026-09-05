"""Behavioral parity checks for every name in :mod:`picop.hot`."""

from __future__ import annotations

from array import array as Array

import pytest

import picop.hot as hot
from picop.hot import (
    ansi_fg8,
    ansi_strip,
    ansi_wrap,
    array_eq,
    array_ne,
    bytearray_contains,
    bytearray_eq,
    bytearray_ne,
    bytes_contains,
    bytes_endswith,
    bytes_eq,
    bytes_len,
    bytes_ne,
    bytes_startswith,
    dict_contains,
    dict_get,
    dict_len,
    dict_pop,
    dict_set,
    dict_setdefault,
    list_append,
    list_get,
    list_get_checked,
    list_len,
    memoryview_eq,
    memoryview_ne,
    set_add,
    set_contains,
    str_contains,
    str_eq,
    str_len,
    tuple_get,
    tuple_len,
    tuple_pack2,
)


def test_hot_all_matches_expected_surface() -> None:
    expected = (
        "dict_get",
        "dict_set",
        "dict_len",
        "dict_contains",
        "dict_pop",
        "dict_setdefault",
        "list_len",
        "list_get",
        "list_get_checked",
        "list_append",
        "set_contains",
        "set_add",
        "tuple_len",
        "tuple_get",
        "tuple_pack2",
        "bytes_len",
        "bytes_contains",
        "bytes_eq",
        "bytes_ne",
        "bytes_startswith",
        "bytes_endswith",
        "bytearray_eq",
        "bytearray_ne",
        "bytearray_contains",
        "array_eq",
        "array_ne",
        "memoryview_eq",
        "memoryview_ne",
        "str_len",
        "str_eq",
        "str_contains",
        "ansi_wrap",
        "ansi_fg8",
        "ansi_strip",
    )
    assert hot.__all__ == expected
    for name in expected:
        assert getattr(hot, name) is not None


def test_dict_helpers_match_python() -> None:
    d = {"a": 1}
    assert dict_get(d, "a") == d.get("a") == 1
    assert dict_get(d, "missing") is None
    assert dict_len(d) == len(d) == 1
    assert dict_contains(d, "a") is True
    assert dict_contains(d, "missing") is False

    working: dict[str, object] = {}
    assert dict_set(working, "k", 7) == 0
    assert working == {"k": 7}
    assert dict_setdefault(working, "k", 9) == 7
    assert dict_setdefault(working, "n", 3) == 3
    assert working == {"k": 7, "n": 3}
    assert dict_pop(working, "k") == 7
    assert "k" not in working


def test_list_helpers_match_python() -> None:
    xs: list[object] = [10, 20]
    assert list_len(xs) == len(xs) == 2
    assert list_get(xs, 0) == xs[0] == 10
    assert list_get_checked(xs, 1) == 20
    assert list_append(xs, 30) == 0
    assert xs == [10, 20, 30]


def test_list_get_checked_raises_on_oob() -> None:
    with pytest.raises(IndexError):
        list_get_checked([1], 5)


def test_set_helpers_match_python() -> None:
    s: set[object] = set()
    assert set_add(s, "x") == 0
    assert set_contains(s, "x") is True
    assert set_contains(s, "y") is False


def test_tuple_helpers_match_python() -> None:
    row = ("a", "b", "c")
    assert tuple_len(row) == len(row) == 3
    assert tuple_get(row, 1) == row[1] == "b"
    assert tuple_pack2(1, 2) == (1, 2)


def test_bytes_helpers_match_python() -> None:
    payload = b"ok"
    assert bytes_len(payload) == len(payload) == 2
    assert bytes_contains(b"ab", b"a") is True
    assert bytes_contains(b"ab", b"z") is False
    assert bytes_eq(b"ok", b"ok") is True
    assert bytes_eq(b"ok", b"no") is False
    assert bytes_ne(b"ok", b"no") is True
    assert bytes_ne(b"ok", b"ok") is False
    assert bytes_startswith(b"ok", b"o") is True
    assert bytes_startswith(b"ok", b"x") is False
    assert bytes_endswith(b"ok", b"k") is True
    assert bytes_endswith(b"ok", b"x") is False


def test_bytearray_helpers_match_python() -> None:
    assert bytearray_eq(bytearray(b"ok"), bytearray(b"ok")) is True
    assert bytearray_eq(bytearray(b"ok"), bytearray(b"no")) is False
    assert bytearray_ne(bytearray(b"ok"), bytearray(b"no")) is True
    assert bytearray_ne(bytearray(b"ok"), bytearray(b"ok")) is False
    assert bytearray_contains(bytearray(b"ok"), b"o") is True
    assert bytearray_contains(bytearray(b"ok"), b"x") is False


def test_array_and_memoryview_helpers_match_python() -> None:
    assert array_eq(Array("i", [1, 2]), Array("i", [1, 2])) is True
    assert array_eq(Array("i", [1, 2]), Array("i", [1, 3])) is False
    assert array_ne(Array("i", [1, 2]), Array("i", [1, 3])) is True
    assert array_ne(Array("i", [1, 2]), Array("i", [1, 2])) is False
    assert memoryview_eq(memoryview(b"ok"), memoryview(b"ok")) is True
    assert memoryview_eq(memoryview(b"ok"), memoryview(b"no")) is False
    assert memoryview_ne(memoryview(b"ok"), memoryview(b"no")) is True
    assert memoryview_ne(memoryview(b"ok"), memoryview(b"ok")) is False


def test_str_helpers_match_python() -> None:
    assert str_len("hi") == len("hi") == 2
    assert str_eq("hi", "hi") is True
    assert str_eq("hi", "no") is False
    assert str_contains("abc", "b") is True
    assert str_contains("abc", "z") is False


def test_ansi_helpers_roundtrip() -> None:
    prefix = ansi_fg8(32)
    wrapped = ansi_wrap(prefix, "picop", "\x1b[0m")
    assert "picop" in wrapped
    assert ansi_strip(wrapped) == "picop"
