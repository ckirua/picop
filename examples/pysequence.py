"""Python usage for picop cysequence.

Run: python examples/pysequence.py
"""
from picop import seq_check, seq_concat, seq_eq, seq_get


def main() -> None:
    assert seq_check([1, 2])
    assert seq_get([1, 2, 3], 1) == 2
    assert seq_concat([1], [2]) == [1, 2]
    assert seq_eq([1, 2], [1, 2]) and not seq_eq([1], [2]) and seq_eq([], [])
    assert seq_eq((1, 2), (1, 2)) and not seq_eq((1,), (1, 2)) and seq_eq((), ())
    assert not seq_eq((1, 2), [1, 2]) and not seq_eq((), [])  # same as ``==``
    assert seq_eq("ab", "ab") and not seq_eq("ab", "ba")
    print("ok", seq_get("ab", 0))


if __name__ == "__main__":
    main()
