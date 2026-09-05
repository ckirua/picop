"""Compare public :mod:`cypy` cybool helpers vs plain Python (tier A).

Run: python bench/cybool_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import bool_check, bool_false, bool_from_long, bool_true

from _bench_util import BenchSession


def main() -> None:
    session = BenchSession("cybool — public helpers vs plain Python (tier A)")
    session.header()

    session.section("bool_check  [primary]")
    session.compare("bool_check", bool_check, lambda o: isinstance(o, bool), True, param="True")
    session.compare("bool_check", bool_check, lambda o: isinstance(o, bool), 1, param="int 1")

    session.section("bool_from_long / true / false")
    session.compare("bool_from_long", bool_from_long, bool, 1, param="1→True")
    session.compare("bool_from_long", bool_from_long, bool, 0, param="0→False")
    session.compare("bool_true", bool_true, lambda: True, param="True")
    session.compare("bool_false", bool_false, lambda: False, param="False")

    session.summary()


if __name__ == "__main__":
    main()
