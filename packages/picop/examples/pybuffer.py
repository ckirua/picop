"""Python usage for picop cybuffer.

Run: python examples/pybuffer.py
"""
from array import array

from picop import buf_check, buf_copy_data, buf_eq


def main() -> None:
    src = bytearray(b"abc")
    dest = bytearray(3)
    assert buf_check(src) is True
    assert buf_check(object()) is False
    assert buf_copy_data(dest, src) == 0
    assert bytes(dest) == b"abc"
    assert buf_eq(b"abc", bytearray(b"abc"))
    assert buf_eq(b"", bytearray())
    assert not buf_eq(b"abc", b"abd")
    assert buf_eq(array("B", [1, 2, 3]), bytes([1, 2, 3]))
    assert not buf_eq(array("i", [1]), array("i", [2]))
    print("ok", bytes(dest))


if __name__ == "__main__":
    main()
