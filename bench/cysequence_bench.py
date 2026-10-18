"""Compare public :mod:`cypy` cysequence helpers vs plain Python (tier A).

Depth: check/size, get/str_contains, str_concat/repeat, list/tuple convert.
Run: python bench/cysequence_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    seq_check,
    seq_concat,
    seq_contains,
    seq_count,
    seq_get,
    seq_index,
    seq_len,
    seq_list,
    seq_repeat,
    seq_size,
    seq_slice,
    seq_tuple,
)

from _bench_util import BenchSession

L = [10, 20, 30, 40]
T = (10, 20, 30, 40)
MID = list(range(64))


def main() -> None:
    session = BenchSession("cysequence — public helpers vs plain Python (tier A)")
    session.header()

    session.section("seq_check / seq_size  [primary: seq_get list]")
    session.compare("seq_check", seq_check, lambda o: hasattr(o, "__getitem__"), L, param="list")
    session.compare("seq_check", seq_check, lambda o: hasattr(o, "__getitem__"), 42, param="int")
    session.compare("seq_size", seq_size, len, L, param="list")
    session.compare("seq_len", seq_len, len, L, param="list alias")

    session.section("seq_get / seq_contains / seq_index / seq_count")
    session.compare("seq_get", seq_get, lambda o, i: o[i], L, 0, param="list[0]")
    session.compare("seq_get", seq_get, lambda o, i: o[i], T, 2, param="tuple[2]")
    session.compare("seq_contains", seq_contains, lambda o, v: v in o, L, 20, param="hit")
    session.compare("seq_contains", seq_contains, lambda o, v: v in o, L, 99, param="miss")
    session.compare("seq_index", seq_index, lambda o, v: o.index(v), L, 30, param="index")
    session.compare("seq_count", seq_count, lambda o, v: o.count(v), L, 20, param="count")

    session.section("seq_slice / seq_concat / seq_repeat")
    session.compare("seq_slice", seq_slice, lambda o, a, b: o[a:b], MID, 10, 20, param="mid10")
    session.compare("seq_concat", seq_concat, lambda a, b: a + b, L, [1], param="list+list")
    session.compare("seq_repeat", seq_repeat, lambda o, n: o * n, L, 3, param="*3")

    session.section("seq_list / seq_tuple")
    session.compare("seq_list", seq_list, list, T, param="tuple→list")
    session.compare("seq_tuple", seq_tuple, tuple, L, param="list→tuple")

    session.summary()


if __name__ == "__main__":
    main()
