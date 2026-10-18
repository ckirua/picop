"""Python usage of :func:`picop` dict helpers.

Run: python examples/pydict.py
"""

from picop import (
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
)

PAYLOAD: dict[str, object] = {
    "symbol": "BTCUSDT",
    "baseAsset": "BTC",
    "quoteAsset": "USDT",
    "status": "TRADING",
    "onboardDate": 1_567_010_800_000,
}

def main() -> None:
    assert dict_eq({"a": 1}, {"a": 1}) and not dict_eq({"a": 1}, {"a": 2}) and dict_eq({}, {})
    assert dict_eq({"a": {"b": 1}}, {"a": {"b": 1}}) and not dict_eq({"a": 1}, {"b": 1})
    print(f"dict_len(payload) -> {dict_len(PAYLOAD)!r}")
    for key in ("symbol", "status", "contractType", "onboardDate"):
        print(f"dict_get(payload, {key!r}) -> {dict_get(PAYLOAD, key)!r}")
    print(f"dict_contains(payload, 'status') -> {dict_contains(PAYLOAD, 'status')!r}")

    working = dict(PAYLOAD)
    rc = dict_set(working, "contractType", "PERPETUAL")
    # rc is 0 on success — do not use as bool (`if dict_set(...):` is wrong)
    print(f"dict_set(payload, 'contractType', 'PERPETUAL') -> rc={rc!r}, dict={working!r}")

    working = dict(PAYLOAD)
    rc = dict_update(working, {"contractType": "PERPETUAL", "marginAsset": "USDT"})
    print(f"dict_update(payload, ...) -> rc={rc!r}, dict={working!r}")

    working = dict(PAYLOAD)
    value = dict_setdefault(working, "contractType", "PERPETUAL")
    print(f"dict_setdefault(payload, 'contractType', 'PERPETUAL') -> {value!r}, dict={working!r}")

    copied = dict_copy(PAYLOAD)
    print(f"dict_copy(payload) -> {copied!r}")

    working = dict(PAYLOAD)
    rc = dict_del(working, "status")
    print(f"dict_del(payload, 'status') -> rc={rc!r}, dict={working!r}")

    working = dict(PAYLOAD)
    popped = dict_pop(working, "symbol")
    print(f"dict_pop(payload, 'symbol') -> {popped!r}, dict={working!r}")

    working = dict(PAYLOAD)
    dict_clear(working)
    print(f"dict_clear(payload) -> dict={working!r}")

    assert dict_get(PAYLOAD, "symbol") == PAYLOAD.get("symbol")
    assert dict_get(PAYLOAD, "contractType") is None
    assert dict_contains(PAYLOAD, "status") is True
    assert dict_len(PAYLOAD) == len(PAYLOAD)
    assert dict_copy(PAYLOAD) == PAYLOAD
    assert dict_copy(PAYLOAD) is not PAYLOAD

    setdefault_working: dict[str, object] = {}
    assert dict_setdefault(setdefault_working, "symbol", "BTCUSDT") == "BTCUSDT"
    assert setdefault_working == {"symbol": "BTCUSDT"}
    assert dict_setdefault(setdefault_working, "symbol", "ETHUSDT") == "BTCUSDT"

    update_working = {"symbol": "BTCUSDT"}
    assert dict_update(update_working, {"status": "TRADING"}) == 0
    assert update_working == {"symbol": "BTCUSDT", "status": "TRADING"}

    del_working = dict(PAYLOAD)
    assert dict_del(del_working, "status") == 0
    assert "status" not in del_working

    clear_working = dict(PAYLOAD)
    dict_clear(clear_working)
    assert clear_working == {}

    print("assertions passed")

if __name__ == "__main__":
    main()
