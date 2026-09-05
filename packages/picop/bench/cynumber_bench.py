"""Compare public :mod:`cypy` cynumber helpers vs plain Python (tier A).

Run: python bench/cynumber_bench.py
"""

from __future__ import annotations

import operator
import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    num_abs,
    num_add,
    num_and,
    num_as_ssize,
    num_check,
    num_floordiv,
    num_index,
    num_index_check,
    num_inplace_add,
    num_long,
    num_mod,
    num_mul,
    num_neg,
    num_pow,
    num_truediv,
)

from _bench_util import BenchSession


def main() -> None:
    session = BenchSession("cynumber — public helpers vs plain Python (tier A)")
    session.header()

    session.section("checks  [primary: num_add]")
    session.compare("num_check", num_check, lambda o: hasattr(o, "__add__") or isinstance(o, (int, float, complex)), 7, param="int")
    session.compare("num_check", num_check, lambda o: hasattr(o, "__add__") or isinstance(o, (int, float, complex)), "x", param="str")
    session.compare("num_index_check", num_index_check, lambda o: hasattr(o, "__index__"), 7, param="int")
    session.compare("num_index_check", num_index_check, lambda o: hasattr(o, "__index__"), 1.5, param="float")

    session.section("binary / unary")
    session.compare("num_add", num_add, operator.add, 3, 5, param="3+5")
    session.compare("num_mul", num_mul, operator.mul, 6, 7, param="6*7")
    session.compare("num_truediv", num_truediv, operator.truediv, 7, 2, param="7/2")
    session.compare("num_floordiv", num_floordiv, operator.floordiv, 7, 2, param="7//2")
    session.compare("num_mod", num_mod, operator.mod, 7, 3, param="7%3")
    session.compare("num_and", num_and, operator.and_, 0b1100, 0b1010, param="bitwise")
    session.compare("num_pow", num_pow, pow, 2, 10, None, param="2**10")
    session.compare("num_neg", num_neg, operator.neg, 42, param="-42")
    session.compare("num_abs", num_abs, abs, -42, param="abs")

    session.section("convert / inplace")
    session.compare("num_long", num_long, int, 3.7, param="int(3.7)")
    session.compare("num_index", num_index, operator.index, True, param="index(True)")
    session.compare("num_as_ssize", num_as_ssize, operator.index, 99, param="99")
    session.compare_mutate(
        "num_inplace_add",
        num_inplace_add,
        lambda a, b: operator.iadd(a, b),
        10,
        int,
        3,
        param="10+=3",
    )

    session.summary()


if __name__ == "__main__":
    main()
