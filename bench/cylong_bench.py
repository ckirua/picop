"""Compare public :mod:`picop` cylong helpers vs plain Python (tier A).

Depth: check exact vs bool, from/as roundtrips, overflow tuple.
Run: python bench/cylong_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from picop.cylong import long_is_negative, long_is_positive, long_is_zero
from picop import (
    long_as_double,
    long_as_long,
    long_as_long_overflow,
    long_as_ssize,
    long_check,
    long_check_exact,
    long_from_double,
    long_from_long,
    long_from_ssize,
)

from _bench_util import BenchSession

N = 42



def main() -> None:
    session = BenchSession("cylong — public helpers vs plain Python (tier A)")
    session.header()
    session.section("narrow sign predicates")
    py_zero = lambda x: x == 0
    py_negative = lambda x: x < 0
    py_positive = lambda x: x > 0
    for value in (0, 1, -1, 42):
        session.compare("long_is_zero", long_is_zero, py_zero, value, param=f"small n={value}")
        session.compare("long_is_negative", long_is_negative, py_negative, value, param=f"small n={value}")
        session.compare("long_is_positive", long_is_positive, py_positive, value, param=f"small n={value}")
    for value in (2**100, -(2**100)):
        session.compare("long_is_zero", long_is_zero, py_zero, value, param=f"large n={value.bit_length()}")
        session.compare("long_is_negative", long_is_negative, py_negative, value, param=f"large n={value.bit_length()}")
        session.compare("long_is_positive", long_is_positive, py_positive, value, param=f"large n={value.bit_length()}")
    session.compare("long_is_zero", long_is_zero, py_zero, 42, param="scale n=42")
    session.compare("long_is_negative", long_is_negative, py_negative, 42, param="scale n=42")
    session.compare("long_is_positive", long_is_positive, py_positive, 42, param="scale n=42")

    session.section("long_check  [primary: long_as_long]")
    session.compare("long_check", long_check, lambda o: isinstance(o, int), N, param="int")
    session.compare("long_check", long_check, lambda o: isinstance(o, int), True, param="bool")
    session.compare(
        "long_check_exact",
        long_check_exact,
        lambda o: type(o) is int,
        N,
        param="int",
    )
    session.compare(
        "long_check_exact",
        long_check_exact,
        lambda o: type(o) is int,
        True,
        param="bool",
    )

    session.section("from / as")
    session.compare("long_from_long", long_from_long, int, N, param="42")
    session.compare("long_from_ssize", long_from_ssize, int, N, param="42")
    session.compare("long_from_double", long_from_double, int, 3.9, param="3.9")
    session.compare("long_as_long", long_as_long, int, N, param="42")
    session.compare("long_as_ssize", long_as_ssize, int, N, param="42")
    session.compare("long_as_double", long_as_double, float, N, param="42")
    session.compare(
        "long_as_long_overflow",
        long_as_long_overflow,
        lambda o: (int(o), 0),
        N,
        param="small no overflow",
    )

    session.summary()


if __name__ == "__main__":
    main()
