"""Tier A: range_eq vs plain ``==`` (empty / equiv spans / steps / identity).

Run: python bench/cyrange_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import range_eq

from _bench_util import BenchSession

R5 = range(5)
R5B = range(5)
R6 = range(6)
R_EMPTY = range(0)
R_EMPTY2 = range(1, 1)
R_EQUIV = range(0, 10, 3)
R_EQUIV2 = range(0, 11, 3)  # same sequence
R_STEP2 = range(0, 10, 2)
R_STEP3 = range(0, 10, 3)
R_BIG = range(0, 1_000_000)
R_BIG2 = range(0, 1_000_000)
R_NEG = range(10, 0, -1)
R_NEG2 = range(10, 0, -1)


def py_eq(a: object, b: object) -> bool:
    return a == b


def main() -> None:
    session = BenchSession("cyrange — range_eq vs ``==`` (tier A)")
    session.header()

    session.section("range_eq vs `==`  [primary: equal span]")
    session.compare("range_eq", range_eq, py_eq, R5, R5B, param="eq span")
    session.compare("range_eq", range_eq, py_eq, R5, R6, param="ne span")
    session.compare("range_eq", range_eq, py_eq, R5, R5, param="identity")
    session.compare("range_eq", range_eq, py_eq, R_EMPTY, R_EMPTY2, param="eq empty")
    session.compare("range_eq", range_eq, py_eq, R_EQUIV, R_EQUIV2, param="eq equiv step")
    session.compare("range_eq", range_eq, py_eq, R_STEP2, R_STEP3, param="ne step")
    session.compare("range_eq", range_eq, py_eq, R_BIG, R_BIG2, param="eq large")
    session.compare("range_eq", range_eq, py_eq, R_NEG, R_NEG2, param="eq reversed")

    session.summary()


if __name__ == "__main__":
    main()
