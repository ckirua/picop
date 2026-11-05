"""Compare public :mod:`picop` traceback helpers with plain Python (tier A)."""

from __future__ import annotations

import sys
import types
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from picop import tb_check, tb_depth, tb_frame, tb_lasti, tb_lineno, tb_next  # noqa: E402
from _bench_util import BenchSession  # noqa: E402


def make_traceback():
    def leaf():
        raise ValueError("benchmark traceback")

    def mid():
        leaf()

    def top():
        mid()

    try:
        top()
    except ValueError:
        return sys.exc_info()[2]
    raise AssertionError("unreachable")


def py_depth(tb):
    n = 0
    while tb is not None:
        n += 1
        tb = tb.tb_next
    return n


def main() -> None:
    tb = make_traceback()
    session = BenchSession("cytraceback — public helpers vs plain Python (tier A)")
    session.header()
    session.section("traceback accessors")
    session.compare("tb_check", tb_check, lambda t: isinstance(t, types.TracebackType), tb, param="tb_check")
    session.compare("tb_next", tb_next, lambda t: t.tb_next, tb, param="tb_next")
    session.compare("tb_frame", tb_frame, lambda t: t.tb_frame, tb, param="tb_frame")
    session.compare("tb_lineno", tb_lineno, lambda t: t.tb_lineno, tb, param="tb_lineno")
    session.compare("tb_lasti", tb_lasti, lambda t: t.tb_lasti, tb, param="tb_lasti")
    session.compare("tb_depth", tb_depth, py_depth, tb, param="tb_depth")
    session.summary()


if __name__ == "__main__":
    main()
