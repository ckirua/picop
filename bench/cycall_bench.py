"""Compare public :mod:`picop` call helpers with direct Python calls (tier A).

Run: python bench/cycall_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from picop import call_noargs, call_onearg, call_twoargs

from _bench_util import BenchSession


VALUE = 17
OTHER = 25


def noargs_work() -> int:
    return VALUE + OTHER


def onearg_work(value: int) -> int:
    return value * 3 + OTHER


def twoargs_work(left: int, right: int) -> int:
    return left * 3 + right


def py_noargs(func):
    return func()


def py_onearg(func, arg):
    return func(arg)


def py_twoargs(func, arg0, arg1):
    return func(arg0, arg1)


def main() -> None:
    session = BenchSession("cycall — public helpers vs direct Python calls (tier A)")
    session.header()

    session.section("call helpers — same callable work and arity")
    session.compare("call_noargs", call_noargs, py_noargs, noargs_work, param="zero args")
    session.compare("call_onearg", call_onearg, py_onearg, onearg_work, VALUE, param="one arg")
    session.compare("call_twoargs", call_twoargs, py_twoargs, twoargs_work, VALUE, OTHER, param="two args")

    session.summary()


if __name__ == "__main__":
    main()
