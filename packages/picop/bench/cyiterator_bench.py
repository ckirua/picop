"""Compare public :mod:`cypy` cyiterator helpers vs plain Python (tier A)."""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import iter_check, iter_next

from _bench_util import BenchSession


def main() -> None:
    session = BenchSession("cyiterator — public helpers vs plain Python (tier A)")
    session.header()
    it = iter([1, 2, 3])
    session.section("iter_check  [primary]")
    session.compare("iter_check", iter_check, lambda o: hasattr(o, "__next__"), it, param="iter")
    session.compare("iter_check", iter_check, lambda o: hasattr(o, "__next__"), [1], param="list")
    # next: use fresh iterators each time via mutate pattern — simple one-shot compare on list iter next
    session.compare("iter_next", iter_next, next, iter(range(10**6)), param="range-iter")
    session.summary()


if __name__ == "__main__":
    main()
