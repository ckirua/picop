"""Compare public :mod:`cypy` cylist helpers vs plain Python (tier A).

Depth: index shapes, empty vs small, slice, sort/reverse, AsTuple.
Run: python bench/cylist_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    list_as_tuple,
    list_append,
    list_check,
    list_check_exact,
    list_clear,
    list_copy,
    list_empty,
    list_extend,
    list_get,
    list_get_checked,
    list_get_ref,
    list_insert,
    list_len,
    list_reverse,
    list_set_item,
    list_set_slice,
    list_size,
    list_slice,
    list_sort,
)

from _bench_util import BenchSession

L_SMALL = [10, 20, 30, 40]
L_MID = list(range(64))
EXT = [1, 2, 3]


def py_lget(l: list, i: int) -> object:
    return l[i]


def py_llen(l: list) -> int:
    return len(l)


def py_lsize(l: object) -> int:
    return len(l)  # type: ignore[arg-type]


def py_lcheck(p: object) -> bool:
    return isinstance(p, list)


def py_lcheck_exact(p: object) -> bool:
    return type(p) is list


def py_lempty() -> list:
    return []


def py_lappend(l: list, value: object) -> int:
    l.append(value)
    return 0


def py_linsert(l: list, i: int, value: object) -> int:
    l.insert(i, value)
    return 0


def py_lextend(l: list, iterable: object) -> int:
    l.extend(iterable)  # type: ignore[arg-type]
    return 0


def py_lclear(l: list) -> int:
    l.clear()
    return 0


def py_lcopy(l: list) -> list:
    return l.copy()


def py_lslice(l: list, low: int, high: int) -> list:
    return l[low:high]


def py_lset_slice(l: list, low: int, high: int, itemlist: object) -> int:
    l[low:high] = itemlist  # type: ignore[misc]
    return 0


def py_lsort(l: list) -> int:
    l.sort()
    return 0


def py_lreverse(l: list) -> int:
    l.reverse()
    return 0


def py_las_tuple(l: list) -> tuple:
    return tuple(l)


def py_lset_item(l: list, i: int, value: object) -> int:
    l[i] = value
    return 0


def main() -> None:
    session = BenchSession("cylist — public helpers vs plain Python (tier A)")
    session.header()

    session.section("list_get family  [primary: index=0]")
    session.compare("list_get", list_get, py_lget, L_SMALL, 0, param="index=0")
    session.compare("list_get", list_get, py_lget, L_SMALL, 3, param="index=3")
    session.compare("list_get", list_get, py_lget, L_MID, 32, param="n=64 mid")
    session.compare("list_get_checked", list_get_checked, py_lget, L_SMALL, 0, param="index=0")
    session.compare("list_get_ref", list_get_ref, py_lget, L_SMALL, 0, param="index=0")

    session.section("list_len / list_size / checks / list_empty")
    session.compare("list_len", list_len, py_llen, L_SMALL, param="small")
    session.compare("list_len", list_len, py_llen, L_MID, param="n=64")
    session.compare("list_size", list_size, py_lsize, L_SMALL, param="small")
    session.compare("list_check", list_check, py_lcheck, L_SMALL, param="list")
    session.compare("list_check_exact", list_check_exact, py_lcheck_exact, L_SMALL, param="exact")
    session.compare("list_empty", list_empty, py_lempty, param="empty")

    session.section("mutators (fresh list each call)")

    def c_lappend() -> int:
        return list_append([1, 2], 3)

    def b_lappend() -> int:
        return py_lappend([1, 2], 3)

    def c_linsert() -> int:
        return list_insert([1, 2, 3], 1, 9)

    def b_linsert() -> int:
        return py_linsert([1, 2, 3], 1, 9)

    def c_lextend() -> int:
        return list_extend([1], EXT)

    def b_lextend() -> int:
        return py_lextend([1], EXT)

    def c_lclear() -> int:
        return list_clear([1, 2, 3])

    def b_lclear() -> int:
        return py_lclear([1, 2, 3])

    def c_lcopy() -> list:
        return list_copy(L_SMALL)

    def b_lcopy() -> list:
        return py_lcopy(L_SMALL)

    def c_lset_item() -> int:
        return list_set_item([1, 2, 3], 1, 9)

    def b_lset_item() -> int:
        return py_lset_item([1, 2, 3], 1, 9)

    def c_lset_slice() -> int:
        return list_set_slice([1, 2, 3, 4], 1, 3, [8, 9])

    def b_lset_slice() -> int:
        return py_lset_slice([1, 2, 3, 4], 1, 3, [8, 9])

    def c_lsort() -> int:
        return list_sort([3, 1, 2])

    def b_lsort() -> int:
        return py_lsort([3, 1, 2])

    def c_lreverse() -> int:
        return list_reverse([1, 2, 3])

    def b_lreverse() -> int:
        return py_lreverse([1, 2, 3])

    session.compare("list_append", c_lappend, b_lappend, param="append")
    session.compare("list_insert", c_linsert, b_linsert, param="insert")
    session.compare("list_extend", c_lextend, b_lextend, param="extend")
    session.compare("list_clear", c_lclear, b_lclear, param="clear")
    session.compare("list_copy", c_lcopy, b_lcopy, param="small")
    session.compare("list_set_item", c_lset_item, b_lset_item, param="set")
    session.compare("list_set_slice", c_lset_slice, b_lset_slice, param="slice assign")
    session.compare("list_sort", c_lsort, b_lsort, param="n=3")
    session.compare("list_reverse", c_lreverse, b_lreverse, param="n=3")

    session.section("list_slice / list_as_tuple")
    session.compare("list_slice", list_slice, py_lslice, L_MID, 10, 20, param="n=64 mid10")
    session.compare("list_as_tuple", list_as_tuple, py_las_tuple, L_SMALL, param="small")
    session.compare("list_as_tuple", list_as_tuple, py_las_tuple, L_MID, param="n=64")

    session.summary()


if __name__ == "__main__":
    main()
