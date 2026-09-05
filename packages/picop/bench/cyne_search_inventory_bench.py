"""Tier A inventory: ``*_ne``, contains, startswith/endswith still missing compares.

Run: CPY_BENCH_RUNS=11 python bench/cyne_search_inventory_bench.py
Paste tables into owning ``docs/modules/NNN_*.md`` trackers.
"""

from __future__ import annotations

import sys
from array import array
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    array_ne,
    bytearray_contains,
    bytearray_ne,
    bytes_endswith,
    bytes_ne,
    bytes_startswith,
    memoryview_ne,
)

from _bench_util import BenchSession


def py_ne(a: object, b: object) -> bool:
    return a != b


def main() -> None:
    session = BenchSession("cyne_search — *_ne / startswith / endswith / contains (tier A)")
    session.header()

    EQ_SHORT = b"BTCUSDT"
    EQ_SHORT_NE = b"BTCUSDX"
    EQ_1K = b"a" * 1024
    EQ_1K_NE = b"a" * 1023 + b"b"
    session.section("bytes_ne / bytes_startswith / bytes_endswith")
    session.compare("bytes_ne", bytes_ne, py_ne, EQ_SHORT, EQ_SHORT, param="eq same")
    session.compare("bytes_ne", bytes_ne, py_ne, EQ_SHORT, EQ_SHORT_NE, param="ne same-len")
    session.compare("bytes_ne", bytes_ne, py_ne, EQ_1K, EQ_1K, param="eq 1KiB")
    session.compare("bytes_ne", bytes_ne, py_ne, EQ_1K, EQ_1K_NE, param="ne 1KiB")
    session.compare(
        "bytes_startswith", bytes_startswith, bytes.startswith, EQ_SHORT, b"BTC", param="hit"
    )
    session.compare(
        "bytes_startswith", bytes_startswith, bytes.startswith, EQ_SHORT, b"ETH", param="miss"
    )
    session.compare(
        "bytes_startswith", bytes_startswith, bytes.startswith, EQ_1K, b"aaa", param="hit 1KiB"
    )
    session.compare(
        "bytes_endswith", bytes_endswith, bytes.endswith, EQ_SHORT, b"USDT", param="hit"
    )
    session.compare(
        "bytes_endswith", bytes_endswith, bytes.endswith, EQ_SHORT, b"USDX", param="miss"
    )
    session.compare(
        "bytes_endswith", bytes_endswith, bytes.endswith, EQ_1K, b"aaa", param="hit 1KiB"
    )

    BA = bytearray(EQ_SHORT)
    BA2 = bytearray(EQ_SHORT)
    BAne = bytearray(EQ_SHORT_NE)
    BA1K = bytearray(EQ_1K)
    BA1Kb = bytearray(EQ_1K)
    BA1Kne = bytearray(EQ_1K_NE)
    session.section("bytearray_ne / bytearray_contains")
    session.compare("bytearray_ne", bytearray_ne, py_ne, BA, BA2, param="eq short")
    session.compare("bytearray_ne", bytearray_ne, py_ne, BA, BAne, param="ne short")
    session.compare("bytearray_ne", bytearray_ne, py_ne, BA1K, BA1Kb, param="eq 1KiB")
    session.compare("bytearray_ne", bytearray_ne, py_ne, BA1K, BA1Kne, param="ne 1KiB")
    session.compare(
        "bytearray_contains",
        bytearray_contains,
        lambda h, n: n in h,
        BA,
        b"BTC",
        param="hit",
    )
    session.compare(
        "bytearray_contains",
        bytearray_contains,
        lambda h, n: n in h,
        BA,
        b"ETH",
        param="miss",
    )
    session.compare(
        "bytearray_contains",
        bytearray_contains,
        lambda h, n: n in h,
        BA1K,
        b"aaa",
        param="hit 1KiB",
    )

    AY = array("i", [1, 2, 3, 4, 5])
    AY2 = array("i", [1, 2, 3, 4, 5])
    AYne = array("i", [1, 2, 3, 4, 9])
    AY64 = array("i", range(64))
    AY64b = array("i", range(64))
    AY64ne = array("i", list(range(63)) + [99])
    session.section("array_ne")
    session.compare("array_ne", array_ne, py_ne, AY, AY2, param="eq small")
    session.compare("array_ne", array_ne, py_ne, AY, AYne, param="ne small")
    session.compare("array_ne", array_ne, py_ne, AY64, AY64b, param="eq n=64")
    session.compare("array_ne", array_ne, py_ne, AY64, AY64ne, param="ne n=64")

    MV = memoryview(b"abcdefgh")
    MV2 = memoryview(b"abcdefgh")
    MVne = memoryview(b"abcdefgX")
    MV1K = memoryview(EQ_1K)
    MV1Kb = memoryview(EQ_1K)
    MV1Kne = memoryview(EQ_1K_NE)
    session.section("memoryview_ne")
    session.compare("memoryview_ne", memoryview_ne, py_ne, MV, MV2, param="eq short")
    session.compare("memoryview_ne", memoryview_ne, py_ne, MV, MVne, param="ne short")
    session.compare("memoryview_ne", memoryview_ne, py_ne, MV1K, MV1Kb, param="eq 1KiB")
    session.compare("memoryview_ne", memoryview_ne, py_ne, MV1K, MV1Kne, param="ne 1KiB")

    session.summary()


if __name__ == "__main__":
    main()
