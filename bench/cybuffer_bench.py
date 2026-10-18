"""Compare public :mod:`picop` cybuffer helpers vs plain Python (tier A).

Depth: check hit/miss across types; copy_data bytearray↔bytearray.
Run: python bench/cybuffer_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from array import array

from picop import buf_check, buf_copy_data, buf_itemsize, buf_ndim, buf_nbytes, buf_readonly

from _bench_util import BenchSession

BA = bytearray(b"abcdefgh")
B = b"abcdefgh"
WORDS = array("I", [1, 2, 3, 4])
MULTIDIM = memoryview(bytearray(16)).cast("B", shape=(4, 4))

def py_buf_check(obj: object) -> bool:
    try:
        memoryview(obj)
    except TypeError:
        return False
    return True


def py_buf_copy_data(dest: object, src: object) -> int:
    memoryview(dest)[:] = memoryview(src)  # type: ignore[index]
    return 0


def main() -> None:
    session = BenchSession("cybuffer — public helpers vs plain Python (tier A)")
    session.header()

    session.section("buf_check  [primary: bytearray]")
    session.compare("buf_check", buf_check, py_buf_check, BA, param="bytearray")
    session.compare("buf_check", buf_check, py_buf_check, B, param="bytes")
    session.compare("buf_check", buf_check, py_buf_check, [1, 2], param="list")
    session.compare("buf_check", buf_check, py_buf_check, 42, param="int")

    session.section("buf_copy_data")
    dest = bytearray(8)
    src = bytearray(b"abcdefgh")
    session.compare_mutate(
        "buf_copy_data",
        buf_copy_data,
        py_buf_copy_data,
        dest,
        bytearray,
        src,
        param="ba←ba 8",
    )

    session.section("buf metadata")
    session.compare("buf_itemsize", buf_itemsize, lambda obj: memoryview(obj).itemsize, BA, param="writable bytes")
    session.compare("buf_itemsize", buf_itemsize, lambda obj: memoryview(obj).itemsize, WORDS, param="writable uint")
    session.compare("buf_nbytes", buf_nbytes, lambda obj: memoryview(obj).nbytes, BA, param="writable bytes")
    session.compare("buf_nbytes", buf_nbytes, lambda obj: memoryview(obj).nbytes, WORDS, param="writable uint")
    session.compare("buf_ndim", buf_ndim, lambda obj: memoryview(obj).ndim, BA, param="1-D bytes")
    session.compare("buf_ndim", buf_ndim, lambda obj: memoryview(obj).ndim, MULTIDIM, param="2-D bytes")
    session.compare("buf_readonly", buf_readonly, lambda obj: memoryview(obj).readonly, BA, param="writable")
    session.compare("buf_readonly", buf_readonly, lambda obj: memoryview(obj).readonly, B, param="readonly")

    session.summary()


if __name__ == "__main__":
    main()
