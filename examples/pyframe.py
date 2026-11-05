"""Python usage for picop cyframe.

Run: python examples/pyframe.py
"""
import sys

from picop import frame_back, frame_check, frame_code, frame_lineno, frame_var


def inner():
    value = 42
    return sys._getframe()


def outer():
    return inner()


def main() -> None:
    frame = outer()
    print("frame_check:", frame_check(frame))
    print("frame_lineno:", frame_lineno(frame))
    print("frame_code:", frame_code(frame).co_name)
    print("frame_back:", frame_back(frame))
    print("frame_var:", frame_var(frame, "value"))


if __name__ == "__main__":
    main()
