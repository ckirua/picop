"""Compare public :mod:`cypy` cymethod helpers vs plain Python (tier A).

Run: python bench/cymethod_bench.py
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import method_check, method_get_function, method_new, method_get_self

from _bench_util import BenchSession


class Box:
    def m(self):
        return 1


def main() -> None:
    session = BenchSession("cymethod — public helpers vs plain Python (tier A)")
    session.header()

    box = Box()
    meth = box.m

    session.section("method_check  [primary: method_get_function]")
    session.compare(
        "method_check",
        method_check,
        lambda o: isinstance(o, types.MethodType),
        meth,
        param="bound",
    )
    session.compare(
        "method_check",
        method_check,
        lambda o: isinstance(o, types.MethodType),
        Box.m,
        param="function",
    )
    session.compare("method_get_function", method_get_function, lambda m: m.__func__, meth, param="__func__")
    session.compare("method_get_self", method_get_self, lambda m: m.__self__, meth, param="__self__")
    session.compare("method_new", method_new, types.MethodType, Box.m, box, param="bind")

    session.summary()


if __name__ == "__main__":
    main()
