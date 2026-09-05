"""Compact Core container helper checks (dict/list/set/tuple/bytes/str)."""

from __future__ import annotations

from picop import (
    bytes_contains,
    bytes_eq,
    bytes_len,
    bytes_ne,
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
