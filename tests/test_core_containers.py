"""Compact Core container helper checks (dict/frozendict/list/set/tuple/bytes/str)."""

from __future__ import annotations

import builtins
from collections import defaultdict

import pytest

from picop import (
    UnicodeWriter,
    anydict_check,
    anydict_check_exact,
    anydict_len,
    bytes_contains,
    bytes_eq,
    bytes_len,
    bytes_ne,
    dict_check,
    dict_clear,
    dict_contains,
    dict_copy,
    dict_del,
    dict_eq,
    dict_get,
    dict_len,
    dict_pop,
    dict_set,
    dict_setdefault,
    dict_update,
    frozendict_check,
    frozendict_check_exact,
    frozendict_empty,
    frozendict_new,
    list_append,
    list_clear,
    list_copy,
    list_eq,
    list_extend,
    list_get,
    list_insert,
    list_len,
    set_add,
    set_clear,
    set_contains,
    set_copy,
    set_discard,
    set_eq,
    set_len,
    set_update,
    str_contains,
    str_eq,
    str_len,
    tuple_eq,
    tuple_get,
    tuple_len,
    tuple_pack2,
    tuple_slice,
    UnicodeWriter,
)


def test_dict_success_paths_and_set_return_code() -> None:
    payload = {"symbol": "BTCUSDT", "status": "TRADING"}
    assert dict_eq(payload, {"symbol": "BTCUSDT", "status": "TRADING"})
    assert not dict_eq(payload, {"symbol": "ETHUSDT"})
    assert dict_len(payload) == len(payload)
    assert dict_get(payload, "symbol") == "BTCUSDT"
    assert dict_get(payload, "missing") is None
    assert dict_contains(payload, "status") is True
    assert dict_copy(payload) == payload
    assert dict_copy(payload) is not payload

    working: dict[str, object] = {}
    rc = dict_set(working, "k", 1)
    assert rc == 0
    assert not rc  # 0 is falsy — do not treat success as True
    assert working == {"k": 1}
    assert dict_setdefault(working, "k", 9) == 1
    assert dict_setdefault(working, "n", 2) == 2
    assert dict_update(working, {"n": 3, "m": 4}) == 0
    assert working == {"k": 1, "n": 3, "m": 4}
    assert dict_del(working, "m") == 0
    assert "m" not in working
    assert dict_pop(working, "k") == 1
    dict_clear(working)
    assert working == {}


def test_list_success_paths_and_append_return_code() -> None:
    symbols = ["BTCUSDT", "ETHUSDT"]
    assert list_eq(symbols, ["BTCUSDT", "ETHUSDT"])
    assert not list_eq(symbols, ["BTCUSDT"])
    assert list_len(symbols) == 2
    assert list_get(symbols, 0) == "BTCUSDT"
    assert list_copy(symbols) == symbols
    assert list_copy(symbols) is not symbols

    working: list[object] = []
    assert list_append(working, "x") == 0
    assert working == ["x"]
    assert list_insert(working, 0, "y") == 0
    assert working == ["y", "x"]
    assert list_extend(working, ["z"]) == 0
    assert working == ["y", "x", "z"]
    assert list_clear(working) == 0
    assert working == []


def test_set_success_paths_and_add_return_code() -> None:
    symbols = {"BTCUSDT", "ETHUSDT"}
    assert set_eq(symbols, {"ETHUSDT", "BTCUSDT"})
    assert not set_eq(symbols, {"SOLUSDT"})
    assert set_len(symbols) == 2
    assert set_contains(symbols, "BTCUSDT") is True
    assert set_contains(symbols, "XRPUSDT") is False
    assert set_copy(symbols) == symbols
    assert set_copy(symbols) is not symbols

    working: set[object] = set()
    assert set_add(working, "a") == 0
    assert working == {"a"}
    assert set_discard(working, "a") == 1
    assert set_discard(working, "a") == 0
    assert set_update(working, ["b", "c"]) == 0
    assert working == {"b", "c"}
    assert set_clear(working) == 0
    assert working == set()


def test_tuple_success_paths() -> None:
    row = ("BTCUSDT", "TRADING", "SPOT")
    assert tuple_eq(row, ("BTCUSDT", "TRADING", "SPOT"))
    assert not tuple_eq(row, ("ETHUSDT",))
    assert tuple_len(row) == 3
    assert tuple_get(row, 1) == "TRADING"
    assert tuple_slice(row, 0, 2) == ("BTCUSDT", "TRADING")
    assert tuple_pack2(1, 2) == (1, 2)


def test_bytes_success_paths() -> None:
    payload = b"BTCUSDT"
    assert bytes_len(payload) == len(payload)
    assert bytes_contains(payload, b"USDT") is True
    assert bytes_contains(payload, b"ETH") is False
    assert bytes_eq(payload, b"BTCUSDT") is True
    assert bytes_eq(payload, b"ETHUSDT") is False
    assert bytes_ne(payload, b"ETHUSDT") is True
    assert bytes_ne(payload, b"BTCUSDT") is False


def test_str_success_paths() -> None:
    symbol = "BTCUSDT"
    assert str_len(symbol) == len(symbol)
    assert str_eq(symbol, "BTCUSDT") is True
    assert str_eq(symbol, "ETHUSDT") is False
    assert str_contains(symbol, "USDT") is True
    assert str_contains(symbol, "ETH") is False


def test_frozendict_checks_distinguish_dict_from_frozendict() -> None:
    if not hasattr(builtins, "frozendict"):
        # 3.14: no frozendict type, so every check must be False, never a
        # silent dict substitution.
        assert frozendict_check({"a": 1}) is False
        assert frozendict_check_exact({"a": 1}) is False
        assert anydict_check({"a": 1}) is True
        assert anydict_check_exact({"a": 1}) is True
        assert anydict_len({"a": 1}) == 1
        return

    frozen = builtins.frozendict({"symbol": "BTCUSDT"})
    subclass = type("FrozenSub", (builtins.frozendict,), {})
    assert frozendict_check(frozen) is True
    assert frozendict_check_exact(frozen) is True
    assert frozendict_check(subclass()) is True
    assert frozendict_check_exact(subclass()) is False
    # frozendict is not a dict subclass, so the dict checks must reject it
    assert frozendict_check({"a": 1}) is False
    assert frozendict_check(1) is False
    assert anydict_check(frozen) is True
    assert anydict_check_exact(frozen) is True
    assert anydict_check(defaultdict(int, {"a": 1})) is True
    assert anydict_check_exact(defaultdict(int, {"a": 1})) is False
    assert anydict_len(frozen) == len(frozen)
    with pytest.raises(TypeError):
        anydict_len([1, 2])
    with pytest.raises(TypeError):
        dict_copy(frozen)


def test_frozendict_new_and_empty_semantics() -> None:
    if not hasattr(builtins, "frozendict"):
        pytest.skip("frozendict constructors need CPython 3.15+")

    source = {"symbol": "BTCUSDT", "status": "TRADING"}
    made = frozendict_new(source)
    assert frozendict_check_exact(made)
    assert dict_check(made) is False
    assert len(made) == 2
    assert made["symbol"] == "BTCUSDT"

    # Re-wrapping a frozendict is a refcount bump, not a copy.
    assert frozendict_new(made) is made

    # A real copy needs an iterable.
    copy = frozendict_new(dict(made))
    assert copy is not made
    assert copy == made

    empty = frozendict_empty()
    assert len(empty) == 0 and frozendict_check_exact(empty)
    with pytest.raises(TypeError):
        frozendict_new(None)

    with pytest.raises(TypeError):
        made["status"] = "CLOSED"
    with pytest.raises(TypeError):
        frozendict_new(1)


def test_unicode_writer_finish() -> None:
    writer = UnicodeWriter(32)
    writer.write("hello")
    writer.write(" world")
    assert writer.finish() == "hello world"


def test_unicode_writer_substring_and_repr() -> None:
    writer = UnicodeWriter()
    writer.write_substring("hello world", 6)
    writer.write_repr({"x": 1})
    assert writer.finish() == "world{'x': 1}"


def test_unicode_writer_utf8_bytes() -> None:
    writer = UnicodeWriter()
    writer.write_utf8("café".encode("utf-8"))
    assert writer.finish() == "café"


def test_unicode_writer_context_manager() -> None:
    with UnicodeWriter() as writer:
        writer.write("context")
    with pytest.raises(RuntimeError, match="already finished"):
        writer.finish()


def test_unicode_writer_double_finish_raises() -> None:
    writer = UnicodeWriter()
    writer.finish()
    with pytest.raises(RuntimeError, match="already finished"):
        writer.finish()


def test_unicode_writer_empty_finish() -> None:
    assert UnicodeWriter().finish() == ""


def test_unicode_writer_char_mixed() -> None:
    writer = UnicodeWriter()
    writer.write("ab")
    writer.write_char(ord("c"))
    writer.write_ascii("def")
    assert writer.finish() == "abcdef"
