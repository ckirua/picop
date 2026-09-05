"""Tier A: deque_eq vs plain ``==`` (scale + identity + unequal).

Run: python bench/cydeque_bench.py
"""

from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import deque_eq

from _bench_util import BenchSession

D_EMPTY = deque()
D_EMPTY2 = deque()
D_SMALL = deque([1, 2, 3, 4, 5])
D_SMALL_EQ = deque([1, 2, 3, 4, 5])
D_SMALL_NE = deque([1, 2, 3, 4, 6])
D_MID = deque(range(64))
D_MID_EQ = deque(range(64))
D_MID_NE = deque(list(range(63)) + [99])
D_NEST = deque([[1, 2], [3, 4]])
D_NEST_EQ = deque([[1, 2], [3, 4]])


def py_eq(a: object, b: object) -> bool:
    return a == b


def main() -> None:
    session = BenchSession("cydeque — deque_eq vs ``==`` (tier A)")
    session.header()

    session.section("deque_eq vs `==`  [primary: small equal]")
    session.compare("deque_eq", deque_eq, py_eq, D_SMALL, D_SMALL_EQ, param="eq small")
    session.compare("deque_eq", deque_eq, py_eq, D_SMALL, D_SMALL_NE, param="ne small")
    session.compare("deque_eq", deque_eq, py_eq, D_SMALL, D_SMALL, param="identity")
    session.compare("deque_eq", deque_eq, py_eq, D_EMPTY, D_EMPTY2, param="eq empty")
    session.compare("deque_eq", deque_eq, py_eq, D_MID, D_MID_EQ, param="eq n=64")
    session.compare("deque_eq", deque_eq, py_eq, D_MID, D_MID_NE, param="ne n=64")
    session.compare("deque_eq", deque_eq, py_eq, D_NEST, D_NEST_EQ, param="eq nested")

    session.summary()


if __name__ == "__main__":
    main()
