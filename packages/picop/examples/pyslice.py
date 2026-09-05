"""Python usage for picop cyslice.

Run: python examples/pyslice.py
"""
from picop import slice_check, slice_eq, slice_new, slice_unpack
from picop.buffers import slice_eq as buffers_slice_eq


def main() -> None:
    s = slice_new(1, 10, 2)
    assert slice_check(s)
    start, stop, step = slice_unpack(s)
    assert (start, stop, step) == (1, 10, 2)
    assert slice_eq(s, slice(1, 10, 2)) and not slice_eq(s, slice(1, 10, 3))
    assert slice_eq(slice(None), slice(None, None, None))
    assert not slice_eq(slice(1, 2), slice(1, 2, 1))  # None step != 1
    assert not slice_eq(slice(None, 10), slice(0, 10))  # None start != 0
    assert buffers_slice_eq(s, slice(1, 10, 2))
    print("ok", start, stop, step)


if __name__ == "__main__":
    main()
