"""Compare public :mod:`picop` cymemoryview helpers vs plain Python (tier A).

Depth: check hit/miss, from_object shapes, contiguous C/F.
Run: python bench/cymemoryview_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from picop import (
    memoryview_check,
    memoryview_from_object,
    memoryview_get_contiguous,
    memoryview_itemsize,
    memoryview_ndim,
    memoryview_nbytes,
    memoryview_readonly,
)

from _bench_util import BenchSession

BA = bytearray(b"abcdefgh")
B = b"abcdefgh"
MV = memoryview(BA)
WORDS = memoryview(bytearray(16)).cast("I")
MULTIDIM = memoryview(bytearray(16)).cast("B", shape=(4, 4))

def py_mvcheck(p: object) -> bool:
    return isinstance(p, memoryview)


def py_mvfrom_object(obj: object) -> memoryview:
    return memoryview(obj)


def py_mvget_contiguous(obj: object, buffertype: int = 0x100, order: str = "C") -> memoryview:
    # PyBUF_READ = 0x100; plain Python uses memoryview(...).cast / tobytes path.
    mv = memoryview(obj)
    if order == "C":
        return mv if mv.contiguous else memoryview(mv.tobytes())
    return memoryview(bytes(mv))  # force materialize for non-C baseline cost


def main() -> None:
    session = BenchSession("cymemoryview — public helpers vs plain Python (tier A)")
    session.header()

    session.section("memoryview_check  [primary: memoryview hit]")
    session.compare("memoryview_check", memoryview_check, py_mvcheck, MV, param="memoryview")
    session.compare("memoryview_check", memoryview_check, py_mvcheck, BA, param="bytearray")

    session.section("memoryview_from_object")
    session.compare("memoryview_from_object", memoryview_from_object, py_mvfrom_object, BA, param="bytearray")
    session.compare("memoryview_from_object", memoryview_from_object, py_mvfrom_object, B, param="bytes")

    session.section("memoryview_get_contiguous")
    session.compare(
        "memoryview_get_contiguous",
        memoryview_get_contiguous,
        py_mvget_contiguous,
        BA,
        param="bytearray C",
    )
    session.compare(
        "memoryview_get_contiguous",
        memoryview_get_contiguous,
        py_mvget_contiguous,
        B,
        param="bytes C",
    )

    session.section("memoryview metadata")
    session.compare("memoryview_itemsize", memoryview_itemsize, lambda mv: mv.itemsize, MV, param="writable bytes")
    session.compare("memoryview_itemsize", memoryview_itemsize, lambda mv: mv.itemsize, WORDS, param="writable uint")
    session.compare("memoryview_nbytes", memoryview_nbytes, lambda mv: mv.nbytes, MV, param="writable bytes")
    session.compare("memoryview_nbytes", memoryview_nbytes, lambda mv: mv.nbytes, WORDS, param="writable uint")
    session.compare("memoryview_ndim", memoryview_ndim, lambda mv: mv.ndim, MV, param="1-D bytes")
    session.compare("memoryview_ndim", memoryview_ndim, lambda mv: mv.ndim, MULTIDIM, param="2-D bytes")
    session.compare("memoryview_readonly", memoryview_readonly, lambda mv: mv.readonly, MV, param="writable")
    session.compare("memoryview_readonly", memoryview_readonly, lambda mv: mv.readonly, memoryview(B), param="readonly")

    session.summary()


if __name__ == "__main__":
    main()
