"""Tier A inventory: ``str_cmp`` / ``str_lt``/``le``/``gt``/``ge`` / ``str_check`` / ``str_is``.

Run: CPY_BENCH_RUNS=11 python bench/cystr_order_inventory_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import str_check, str_cmp, str_ge, str_gt, str_is, str_le, str_lt

from _bench_util import BenchSession

A = "hello"
B = "hallo"
C = "hello"
LONG = "a" * 64 + "z"
LONG2 = "a" * 64 + "y"
NON_ASCII = "café"
NON_ASCII2 = "cafë"


def py_cmp(a: str, b: str) -> int:
    return (a > b) - (a < b)


def main() -> None:
    session = BenchSession("cystr_order — str_cmp / ordering / check (tier A)")
    session.header()

    session.section("str_cmp / ordering")
    session.compare("str_cmp", str_cmp, py_cmp, A, C, param="eq")
    session.compare("str_cmp", str_cmp, py_cmp, A, B, param="gt/lt ascii")
    session.compare("str_cmp", str_cmp, py_cmp, LONG, LONG2, param="long")
    session.compare("str_cmp", str_cmp, py_cmp, NON_ASCII, NON_ASCII2, param="non-ascii")
    session.compare("str_lt", str_lt, lambda a, b: a < b, A, B, param="lt")
    session.compare("str_lt", str_lt, lambda a, b: a < b, B, A, param="lt false")
    session.compare("str_le", str_le, lambda a, b: a <= b, A, C, param="le eq")
    session.compare("str_le", str_le, lambda a, b: a <= b, A, B, param="le")
    session.compare("str_gt", str_gt, lambda a, b: a > b, A, B, param="gt")
    session.compare("str_gt", str_gt, lambda a, b: a > b, B, A, param="gt false")
    session.compare("str_ge", str_ge, lambda a, b: a >= b, A, C, param="ge eq")
    session.compare("str_ge", str_ge, lambda a, b: a >= b, A, B, param="ge")

    session.section("str_check / str_is")
    session.compare("str_check", str_check, lambda o: isinstance(o, str), A, param="str")
    session.compare("str_check", str_check, lambda o: isinstance(o, str), 1, param="int")
    session.compare("str_is", str_is, lambda o: type(o) is str, A, param="exact")
    session.compare("str_is", str_is, lambda o: type(o) is str, 1, param="int")

    session.summary()


if __name__ == "__main__":
    main()
