"""Tier A inventory: every public ``*_eq`` still missing from module harnesses.

Run: CPY_BENCH_RUNS=11 python bench/cyeq_inventory_bench.py
Paste tables into the matching ``docs/modules/NNN_*.md`` trackers.
"""

from __future__ import annotations

import datetime as dt
import sys
from array import array
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    array_eq,
    bool_eq,
    buf_eq,
    bytearray_eq,
    cell_eq,
    complex_eq,
    dict_eq,
    dt_date_eq,
    dt_datetime_eq,
    dt_time_eq,
    dt_timedelta_eq,
    float_eq,
    frozenset_eq,
    int_eq,
    list_eq,
    long_eq,
    map_eq,
    memoryview_eq,
    num_eq,
    seq_eq,
    set_eq,
    slice_eq,
    tuple_eq,
    type_eq,
    unicode_eq,
)

from _bench_util import BenchSession


def py_eq(a: object, b: object) -> bool:
    return a == b


def main() -> None:
    session = BenchSession("cyeq_inventory — remaining *_eq vs ``==`` (tier A)")
    session.header()

    # --- containers ---
    L = [1, 2, 3, 4, 5]
    L2 = [1, 2, 3, 4, 5]
    Lne = [1, 2, 3, 4, 6]
    L64 = list(range(64))
    L64b = list(range(64))
    T = (1, 2, 3, 4, 5)
    T2 = (1, 2, 3, 4, 5)
    Tne = (1, 2, 3, 4, 6)
    T64 = tuple(range(64))
    T64b = tuple(range(64))
    session.section("list_eq / tuple_eq / seq_eq")
    session.compare("list_eq", list_eq, py_eq, L, L2, param="eq small")
    session.compare("list_eq", list_eq, py_eq, L, Lne, param="ne small")
    session.compare("list_eq", list_eq, py_eq, L, L, param="identity")
    session.compare("list_eq", list_eq, py_eq, L64, L64b, param="eq n=64")
    session.compare("tuple_eq", tuple_eq, py_eq, T, T2, param="eq small")
    session.compare("tuple_eq", tuple_eq, py_eq, T, Tne, param="ne small")
    session.compare("tuple_eq", tuple_eq, py_eq, T, T, param="identity")
    session.compare("tuple_eq", tuple_eq, py_eq, T64, T64b, param="eq n=64")
    session.compare("seq_eq", seq_eq, py_eq, L, L2, param="list eq")
    session.compare("seq_eq", seq_eq, py_eq, T, L2, param="tuple↔list eq")
    session.compare("seq_eq", seq_eq, py_eq, L, Lne, param="list ne")

    D = {"a": 1, "b": 2, "c": 3}
    D2 = {"a": 1, "b": 2, "c": 3}
    Dne = {"a": 1, "b": 2, "c": 9}
    S = {1, 2, 3, 4, 5}
    S2 = {1, 2, 3, 4, 5}
    Sne = {1, 2, 3, 4, 9}
    FS = frozenset(S)
    FS2 = frozenset(S2)
    session.section("dict_eq / set_eq / frozenset_eq / map_eq")
    session.compare("dict_eq", dict_eq, py_eq, D, D2, param="eq small")
    session.compare("dict_eq", dict_eq, py_eq, D, Dne, param="ne small")
    session.compare("dict_eq", dict_eq, py_eq, D, D, param="identity")
    session.compare("set_eq", set_eq, py_eq, S, S2, param="eq small")
    session.compare("set_eq", set_eq, py_eq, S, Sne, param="ne small")
    session.compare("frozenset_eq", frozenset_eq, py_eq, FS, FS2, param="eq")
    session.compare("frozenset_eq", frozenset_eq, py_eq, FS, frozenset(Sne), param="ne")
    session.compare("map_eq", map_eq, py_eq, D, D2, param="dict eq")
    session.compare("map_eq", map_eq, py_eq, D, Dne, param="dict ne")

    # --- buffers ---
    BA = bytearray(b"BTCUSDT")
    BA2 = bytearray(b"BTCUSDT")
    BAne = bytearray(b"ETHUSDT")
    BA1K = bytearray(b"a" * 1024)
    BA1Kb = bytearray(b"a" * 1024)
    AY = array("i", [1, 2, 3, 4, 5])
    AY2 = array("i", [1, 2, 3, 4, 5])
    AYne = array("i", [1, 2, 3, 4, 9])
    AY64 = array("i", range(64))
    AY64b = array("i", range(64))
    MV = memoryview(b"abcdefgh")
    MV2 = memoryview(b"abcdefgh")
    MVne = memoryview(b"abcdefgX")
    BUF = b"abcdefgh"
    session.section("bytearray_eq / array_eq / memoryview_eq / buf_eq")
    session.compare("bytearray_eq", bytearray_eq, py_eq, BA, BA2, param="eq short")
    session.compare("bytearray_eq", bytearray_eq, py_eq, BA, BAne, param="ne short")
    session.compare("bytearray_eq", bytearray_eq, py_eq, BA1K, BA1Kb, param="eq 1KiB")
    session.compare("array_eq", array_eq, py_eq, AY, AY2, param="eq small")
    session.compare("array_eq", array_eq, py_eq, AY, AYne, param="ne small")
    session.compare("array_eq", array_eq, py_eq, AY64, AY64b, param="eq n=64")
    session.compare("memoryview_eq", memoryview_eq, py_eq, MV, MV2, param="eq")
    session.compare("memoryview_eq", memoryview_eq, py_eq, MV, MVne, param="ne")
    session.compare("buf_eq", buf_eq, py_eq, BUF, bytearray(BUF), param="bytes↔ba")
    session.compare("buf_eq", buf_eq, py_eq, MV, memoryview(BUF), param="mv↔mv")
    session.compare("buf_eq", buf_eq, py_eq, BUF, b"abcdefgX", param="ne")

    # --- scalars ---
    session.section("bool_eq / float_eq / long_eq / int_eq / complex_eq / num_eq")
    session.compare("bool_eq", bool_eq, py_eq, True, True, param="True")
    session.compare("bool_eq", bool_eq, py_eq, True, False, param="ne")
    session.compare("float_eq", float_eq, py_eq, 1.5, 1.5, param="eq")
    session.compare("float_eq", float_eq, py_eq, 1.5, 1.6, param="ne")
    session.compare("long_eq", long_eq, py_eq, 42, 42, param="eq small")
    session.compare("long_eq", long_eq, py_eq, 42, 43, param="ne")
    session.compare("long_eq", long_eq, py_eq, 2**100, 2**100, param="eq big")
    session.compare("int_eq", int_eq, py_eq, 7, 7, param="eq")
    session.compare("complex_eq", complex_eq, py_eq, 1 + 2j, 1 + 2j, param="eq")
    session.compare("complex_eq", complex_eq, py_eq, 1 + 2j, 1 + 3j, param="ne")
    session.compare("num_eq", num_eq, py_eq, 3, 3.0, param="int↔float")
    session.compare("num_eq", num_eq, py_eq, 3, 4, param="ne")

    # --- datetime / slice / type / cell / unicode ---
    d1 = dt.date(2026, 7, 22)
    d2 = dt.date(2026, 7, 22)
    dne = dt.date(2026, 7, 23)
    t1 = dt.time(12, 30, 0)
    t2 = dt.time(12, 30, 0)
    dt1 = dt.datetime(2026, 7, 22, 12, 30)
    dt2 = dt.datetime(2026, 7, 22, 12, 30)
    td1 = dt.timedelta(days=1, seconds=30)
    td2 = dt.timedelta(days=1, seconds=30)
    sl1 = slice(1, 10, 2)
    sl2 = slice(1, 10, 2)
    slne = slice(1, 10, 3)
    session.section("datetime / slice_eq / type_eq / cell_eq / unicode_eq")
    session.compare("dt_date_eq", dt_date_eq, py_eq, d1, d2, param="eq")
    session.compare("dt_date_eq", dt_date_eq, py_eq, d1, dne, param="ne")
    session.compare("dt_time_eq", dt_time_eq, py_eq, t1, t2, param="eq")
    session.compare("dt_datetime_eq", dt_datetime_eq, py_eq, dt1, dt2, param="eq")
    session.compare("dt_timedelta_eq", dt_timedelta_eq, py_eq, td1, td2, param="eq")
    session.compare("slice_eq", slice_eq, py_eq, sl1, sl2, param="eq")
    session.compare("slice_eq", slice_eq, py_eq, sl1, slne, param="ne")
    session.compare("type_eq", type_eq, py_eq, int, int, param="identity")
    session.compare("type_eq", type_eq, py_eq, int, str, param="ne")

    def _outer(x: object) -> object:
        def _inner() -> object:
            return x

        return _inner

    c1 = _outer(1).__closure__[0]  # type: ignore[index]
    c1b = _outer(1).__closure__[0]  # type: ignore[index]
    c2 = _outer(2).__closure__[0]  # type: ignore[index]
    session.compare("cell_eq", cell_eq, py_eq, c1, c1, param="identity")
    session.compare("cell_eq", cell_eq, py_eq, c1, c1b, param="same value")
    session.compare("cell_eq", cell_eq, py_eq, c1, c2, param="ne")

    session.compare("unicode_eq", unicode_eq, py_eq, "hello", "hello", param="ascii eq")
    session.compare("unicode_eq", unicode_eq, py_eq, "hello", "hallo", param="ascii ne")
    session.compare("unicode_eq", unicode_eq, py_eq, "héllo", "héllo", param="non-ascii eq")

    session.summary()


if __name__ == "__main__":
    main()
