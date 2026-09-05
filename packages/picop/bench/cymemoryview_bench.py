"""Compare public :mod:`cypy` cymemoryview helpers vs plain Python (tier A).

Depth: check hit/miss, from_object shapes, contiguous C/F.
Run: python bench/cymemoryview_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import memoryview_check, memoryview_from_object, memoryview_get_contiguous

from _bench_util import BenchSession

BA = bytearray(b"abcdefgh")
B = b"abcdefgh"
MV = memoryview(BA)


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

    session.summary()


if __name__ == "__main__":
    main()
