"""Python usage for picop cydeque.

Run: python examples/pydeque.py
"""
from collections import deque

from picop import deque_eq


def main() -> None:
    a = deque([1, 2, 3])
    b = deque([1, 2, 3])
    c = deque([1, 2, 4])
    assert deque_eq(a, b) and not deque_eq(a, c)
    assert deque_eq(a, a)
    assert deque_eq(deque(), deque())
    assert deque_eq(a, b) == (a == b)
    print("ok", list(a))


if __name__ == "__main__":
    main()
