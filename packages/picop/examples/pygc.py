"""Python usage for picop cygc.

Run: python examples/pygc.py
"""
from picop import gc_is_enabled, gc_collect

def main() -> None:
    assert isinstance(gc_is_enabled(), bool)
    n = gc_collect()
    assert isinstance(n, int)
    print("ok", gc_is_enabled(), n)

if __name__ == "__main__":
    main()
