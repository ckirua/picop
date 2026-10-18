"""Compare public :mod:`cypy` cyfunction helpers vs plain Python (tier A).

Run: python bench/cyfunction_bench.py
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import func_check, func_get_code, func_get_defaults, func_get_globals

from _bench_util import BenchSession


def _sample(x=1):
    return x


def main() -> None:
    session = BenchSession("cyfunction — public helpers vs plain Python (tier A)")
    session.header()

    session.section("func_check  [primary: func_get_code]")
    session.compare(
        "func_check",
        func_check,
        lambda o: isinstance(o, types.FunctionType),
        _sample,
        param="func",
    )
    session.compare(
        "func_check",
        func_check,
        lambda o: isinstance(o, types.FunctionType),
        len,
        param="builtin",
    )
    session.compare("func_get_code", func_get_code, lambda f: f.__code__, _sample, param="__code__")
    session.compare(
        "func_get_globals",
        func_get_globals,
        lambda f: f.__globals__,
        _sample,
        param="__globals__",
    )
    session.compare(
        "func_get_defaults",
        func_get_defaults,
        lambda f: f.__defaults__,
        _sample,
        param="__defaults__",
    )

    session.summary()


if __name__ == "__main__":
    main()
