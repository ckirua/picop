"""Python usage for picop cycodecs.

Run: python examples/pycodecs.py
"""
from picop import codec_known, codec_encode, codec_decode

def main() -> None:
    assert codec_known(b"utf-8") is True
    enc = codec_encode("café", b"utf-8")
    assert enc == "café".encode()
    dec = codec_decode(enc, b"utf-8")
    assert dec == "café"
    print("ok", enc, dec)

if __name__ == "__main__":
    main()
