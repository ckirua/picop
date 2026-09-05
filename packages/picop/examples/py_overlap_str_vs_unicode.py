"""Overlap playbook: ``cystr`` value ops vs ``cyunicode`` encode/intern.

Run: python examples/py_overlap_str_vs_unicode.py
"""

from __future__ import annotations

from picop import (
    str_check,
    str_check_exact,
    str_contains,
    str_eq,
    str_is,
    str_len,
    uintern,
    uutf8_bytes,
)

def main() -> None:
    s = "BTCUSDT"

    # Value ops on str → cystr (Core)
    assert str_len(s) == 7
    assert str_eq(s, "BTCUSDT")
    assert str_contains(s, "USDT")

    # Check pair: subtype vs exact (N3). str_is is the same as str_check_exact.
    assert str_check(s)
    assert str_check_exact(s)
    assert str_is(s) is True
    assert str_is is str_check_exact or str_is(s) == str_check_exact(s)

    # Encode / intern → cyunicode layer (same product family)
    assert uutf8_bytes(s) == b"BTCUSDT"
    interned = uintern(s)
    assert interned is uintern("BTCUSDT")

    print("ok str vs unicode", str_len(s), uutf8_bytes(s))

if __name__ == "__main__":
    main()
