"""Compare public :mod:`picop` sentinel helpers with plain Python calls (tier A).

Run: python bench/cysentinel_bench.py
"""

from __future__ import annotations

import builtins
import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from picop import sentinel_check, sentinel_check_exact, sentinel_new, sentinel_type

from _bench_util import BenchSession


def py_sentinel_check(obj):
    return isinstance(obj, SENT)


def py_sentinel_check_exact(obj):
    return type(obj) is SENT


def py_sentinel_new(name):
    return builtins.sentinel(name)


def py_sentinel_type():
    return builtins.sentinel


def main() -> None:
    if not hasattr(builtins, "sentinel"):
        print("n/a — sentinel is a CPython 3.15+ type")
        return

    global SENT
    SENT = builtins.sentinel
    value = builtins.sentinel("MISS", repr="<MISS>")

    session = BenchSession("cysentinel — public helpers vs plain Python (tier A)")
    session.header()

    session.section("type gates — sentinel")
    session.compare("sentinel_check", sentinel_check, py_sentinel_check, value, param="sentinel hit")
    session.compare("sentinel_check", sentinel_check, py_sentinel_check, None, param="None miss")
    session.compare("sentinel_check_exact", sentinel_check_exact, py_sentinel_check_exact, value, param="sentinel hit")
    session.compare("sentinel_check_exact", sentinel_check_exact, py_sentinel_check_exact, None, param="None miss")

    session.section("construction and lookup — sentinel")
    session.compare("sentinel_new", sentinel_new, py_sentinel_new, "MISS", param="named marker")
    session.compare("sentinel_type", sentinel_type, py_sentinel_type)

    session.summary()


if __name__ == "__main__":
    main()
