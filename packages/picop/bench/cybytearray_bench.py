"""Compare public :mod:`cypy` cybytearray helpers vs plain Python (tier A).

Depth: len shapes, check hit/miss, from_object, str_concat sizes, resize.
Run: python bench/cybytearray_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    bytearray_check,
    bytearray_check_exact,
    bytearray_concat,
    bytearray_from_object,
    bytearray_len,
    bytearray_resize,
    bytearray_size,
)

from _bench_util import BenchSession

BA_SMALL = bytearray(b"abcabc")
BA_MID = bytearray(range(64))
BA_A = bytearray(b"hello")
BA_B = bytearray(b"world")
MV = memoryview(b"xyz")


def py_balen(ba: bytearray) -> int:
    return len(ba)


def py_basize(ba: object) -> int:
    return len(ba)  # type: ignore[arg-type]


def py_bacheck(p: object) -> bool:
    return isinstance(p, bytearray)


def py_bacheck_exact(p: object) -> bool:
    return type(p) is bytearray


def py_bafrom_object(o: object) -> bytearray:
    return bytearray(o)


def py_baconcat(a: object, b: object) -> bytearray:
    return a + b  # type: ignore[operator]


def py_baresize(ba: bytearray, n: int) -> int:
    # Closest plain API: truncate/extend with zeros (Resize reallocates buffer).
    if n < len(ba):
        del ba[n:]
    else:
        ba.extend(b"\x00" * (n - len(ba)))
    return 0


def main() -> None:
    session = BenchSession("cybytearray — public helpers vs plain Python (tier A)")
    session.header()

    session.section("bytearray_len / bytearray_size vs len  [primary: bytearray_len small]")
    session.compare("bytearray_len", bytearray_len, py_balen, BA_SMALL, param="small")
    session.compare("bytearray_len", bytearray_len, py_balen, BA_MID, param="n=64")
    session.compare("bytearray_size", bytearray_size, py_basize, BA_SMALL, param="small")

    session.section("bytearray_check / bytearray_check_exact")
    session.compare("bytearray_check", bytearray_check, py_bacheck, BA_SMALL, param="bytearray")
    session.compare("bytearray_check", bytearray_check, py_bacheck, b"bytes", param="bytes")
    session.compare(
        "bytearray_check_exact",
        bytearray_check_exact,
        py_bacheck_exact,
        BA_SMALL,
        param="bytearray",
    )

    session.section("bytearray_from_object vs bytearray()")
    session.compare(
        "bytearray_from_object",
        bytearray_from_object,
        py_bafrom_object,
        MV,
        param="memoryview",
    )
    session.compare(
        "bytearray_from_object",
        bytearray_from_object,
        py_bafrom_object,
        b"abc",
        param="bytes",
    )

    session.section("bytearray_concat vs +")
    session.compare("bytearray_concat", bytearray_concat, py_baconcat, BA_A, BA_B, param="5+5")
    session.compare(
        "bytearray_concat",
        bytearray_concat,
        py_baconcat,
        BA_MID,
        BA_SMALL,
        param="64+6",
    )

    session.section("bytearray_resize vs extend/del")
    session.compare_mutate(
        "bytearray_resize",
        bytearray_resize,
        py_baresize,
        bytearray(b"abcdefgh"),
        bytearray,
        4,
        param="shrink 8→4",
    )
    session.compare_mutate(
        "bytearray_resize",
        bytearray_resize,
        py_baresize,
        bytearray(b"abcd"),
        bytearray,
        16,
        param="grow 4→16",
    )

    session.summary()


if __name__ == "__main__":
    main()
