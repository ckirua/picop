"""Compare public :mod:`cypy` cyslice helpers vs plain Python (tier A).

Depth: check, new, indices_ex shapes, unpack.
Run: python bench/cyslice_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import slice_check, slice_indices_ex, slice_new, slice_unpack

from _bench_util import BenchSession

SL = slice(1, 10, 2)
SL_NONE = slice(None, None, None)


def py_slcheck(p: object) -> bool:
    return isinstance(p, slice)


def py_slnew(start=None, stop=None, step=None) -> slice:
    return slice(start, stop, step)


def py_slindices_ex(sl: slice, length: int) -> tuple[int, int, int, int]:
    start, stop, step = sl.indices(length)
    # slicelen
    slicelen = max(0, (stop - start + (step - (1 if step > 0 else -1))) // step)
    return (start, stop, step, slicelen)


def py_slunpack(sl: slice) -> tuple[int, int, int]:
    # Approximate: use indices on a huge length then... Unpack is different.
    # Baseline: attribute access + None→sentinel is not identical; use indices(sys.maxsize)
    # Better: match common Python pattern
    def _as_int(x, default):
        return default if x is None else int(x)

    return (_as_int(sl.start, 0), _as_int(sl.stop, 0), _as_int(sl.step, 1))


def main() -> None:
    session = BenchSession("cyslice — public helpers vs plain Python (tier A)")
    session.header()

    session.section("slice_check / slice_new  [primary: slice_indices_ex]")
    session.compare("slice_check", slice_check, py_slcheck, SL, param="slice")
    session.compare("slice_check", slice_check, py_slcheck, 1, param="int")
    session.compare("slice_new", slice_new, py_slnew, 1, 10, 2, param="1:10:2")
    session.compare("slice_new", slice_new, py_slnew, None, None, None, param="::")

    session.section("slice_indices_ex / slice_unpack")
    session.compare("slice_indices_ex", slice_indices_ex, py_slindices_ex, SL, 20, param="1:10:2 len=20")
    session.compare(
        "slice_indices_ex",
        slice_indices_ex,
        py_slindices_ex,
        SL_NONE,
        20,
        param=":: len=20",
    )
    session.compare("slice_unpack", slice_unpack, py_slunpack, SL, param="1:10:2")

    session.summary()


if __name__ == "__main__":
    main()
