"""Python usage for picop cymemoryview.

Run: python examples/pymemoryview.py
"""
from picop import memoryview_check, memoryview_eq, memoryview_from_object, memoryview_ne

def main() -> None:
    mv = memoryview_from_object(b"abc")
    assert memoryview_check(mv)
    assert bytes(mv) == b"abc"
    assert memoryview_eq(mv, memoryview(b"abc"))
    assert not memoryview_eq(mv, memoryview(b"abd"))
    assert memoryview_eq(memoryview(b""), memoryview(b""))
    assert memoryview_ne(mv, memoryview(b"abd")) and not memoryview_ne(mv, memoryview(b"abc"))
    print("ok", bytes(mv))

if __name__ == "__main__":
    main()
