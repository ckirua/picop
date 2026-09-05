"""Python usage for picop cyunicode.

Run: python examples/pyunicode.py

Cimport-only ``unicode_from_string`` / ``uutf8_eq``: see ``bench/tier_b/cyunicode_tb.pyx`` smoke.
"""
from picop import uutf8_bytes, uintern, unicode_eq

def main() -> None:
    b = uutf8_bytes("hi")
    assert b == b"hi"
    s = uintern("phase6")
    assert s is uintern("phase6")
    assert unicode_eq("hi", "hi") and not unicode_eq("hi", "no")
    print("ok", b, s)

if __name__ == "__main__":
    main()
