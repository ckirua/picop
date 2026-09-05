"""Compare public :mod:`cypy` cyfloat helpers vs plain Python (tier A).

Run: python bench/cyfloat_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    float_as_double,
    float_check,
    float_check_exact,
    float_from_double,
    float_from_cstr,
)

from _bench_util import BenchSession

F = 3.14159


def main() -> None:
    session = BenchSession("cyfloat — public helpers vs plain Python (tier A)")
    session.header()

    session.section("float_check  [primary: float_as_double]")
    session.compare("float_check", float_check, lambda o: isinstance(o, float), F, param="float")
    session.compare("float_check", float_check, lambda o: isinstance(o, float), 1, param="int")
    session.compare(
        "float_check_exact",
        float_check_exact,
        lambda o: type(o) is float,
        F,
        param="float",
    )

    session.section("from / as")
    session.compare("float_from_double", float_from_double, float, 2.5, param="2.5")
    session.compare("float_from_cstr", float_from_cstr, float, "2.5", param="'2.5'")
    session.compare("float_as_double", float_as_double, float, F, param="pi")
    session.compare("float_as_double", float_as_double, float, 7, param="int 7")

    session.summary()


if __name__ == "__main__":
    main()
