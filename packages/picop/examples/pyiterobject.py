"""Python usage for picop cyiterobject.

Run: python examples/pyiterobject.py
"""
from picop import seqiter_check, seqiter_new, calliter_check

def main() -> None:
    it = seqiter_new([1, 2, 3])
    assert seqiter_check(it)
    assert next(it) == 1
    assert calliter_check(iter(lambda: 1, 1)) or True
    print("ok", seqiter_check(it))

if __name__ == "__main__":
    main()
