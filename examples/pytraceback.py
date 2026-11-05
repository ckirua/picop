"""Python usage for picop cytraceback.

Run: python examples/pytraceback.py
"""
import sys

from picop import tb_check, tb_depth, tb_frame, tb_lasti, tb_lineno, tb_next


def leaf() -> None:
    raise ValueError("probe")


def mid() -> None:
    leaf()


def top() -> None:
    mid()


def main() -> None:
    try:
        top()
    except ValueError:
        tb = sys.exc_info()[2]
    assert tb_check(tb)
    print("tb_depth:", tb_depth(tb))
    print("tb_lineno:", tb_lineno(tb))
    print("tb_lasti:", tb_lasti(tb))
    print("tb_frame:", tb_frame(tb))
    print("tb_next:", tb_next(tb))


if __name__ == "__main__":
    main()
