"""Compare public :mod:`cypy` cyarray helpers vs plain Python (tier A).

Depth: len, check, copy/clone, extend, zero, resize shapes.
Run: python bench/cyarray_bench.py
"""

from __future__ import annotations

import sys
from array import array
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    array_check,
    array_check_exact,
    array_clone,
    array_copy,
    array_extend,
    array_len,
    array_resize,
    array_resize_smart,
    array_zero,
)

from _bench_util import BenchSession

A_SMALL = array("i", [1, 2, 3, 4])
A_MID = array("i", range(64))
A_EXT = array("i", [10, 20])


def py_aylen(a: array) -> int:
    return len(a)


def py_aycheck(p: object) -> bool:
    return isinstance(p, array)


def py_aycheck_exact(p: object) -> bool:
    return type(p) is array


def py_aycopy(a: array) -> array:
    return array(a.typecode, a)


def py_ayclone(template: array, length: int, zero: bool = True) -> array:
    return array(template.typecode, [0] * length)


def py_ayextend(self: array, other: array) -> int:
    self.extend(other)
    return 0


def py_ayzero(a: array) -> int:
    for i in range(len(a)):
        a[i] = 0
    return 0


def py_ayresize(a: array, n: int) -> int:
    if n < len(a):
        del a[n:]
    else:
        a.extend([0] * (n - len(a)))
    return 0


def _copy_array(a: array) -> array:
    return array(a.typecode, a)


def main() -> None:
    session = BenchSession("cyarray — public helpers vs plain Python (tier A)")
    session.header()

    session.section("array_len vs len  [primary]")
    session.compare("array_len", array_len, py_aylen, A_SMALL, param="small")
    session.compare("array_len", array_len, py_aylen, A_MID, param="n=64")

    session.section("array_check / array_check_exact")
    session.compare("array_check", array_check, py_aycheck, A_SMALL, param="array")
    session.compare("array_check", array_check, py_aycheck, [1, 2], param="list")
    session.compare("array_check_exact", array_check_exact, py_aycheck_exact, A_SMALL, param="array")

    session.section("array_copy / array_clone")
    session.compare("array_copy", array_copy, py_aycopy, A_SMALL, param="small")
    session.compare("array_copy", array_copy, py_aycopy, A_MID, param="n=64")
    session.compare("array_clone", array_clone, py_ayclone, A_SMALL, 8, True, param="clone zero n=8")

    session.section("array_extend / array_zero")
    session.compare_mutate(
        "array_extend",
        array_extend,
        py_ayextend,
        A_SMALL,
        _copy_array,
        A_EXT,
        param="extend +2",
    )
    session.compare_mutate(
        "array_zero",
        array_zero,
        py_ayzero,
        A_MID,
        _copy_array,
        param="zero n=64",
    )

    session.section("array_resize / array_resize_smart")
    session.compare_mutate(
        "array_resize",
        array_resize,
        py_ayresize,
        array("i", range(8)),
        _copy_array,
        4,
        param="shrink 8→4",
    )
    session.compare_mutate(
        "array_resize_smart",
        array_resize_smart,
        py_ayresize,
        array("i", range(4)),
        _copy_array,
        16,
        param="grow 4→16",
    )

    session.summary()


if __name__ == "__main__":
    main()
