"""Compare public :mod:`cypy` cyset helpers vs plain Python (tier A).

Depth: hit/miss str_contains, small vs mid size, frozenset checks, update shapes.
Run: python bench/cyset_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    set_add,
    set_any_check,
    set_any_check_exact,
    set_check,
    set_check_exact,
    set_clear,
    set_contains,
    set_copy,
    set_discard,
    set_empty,
    frozenset_check,
    frozenset_check_exact,
    frozenset_empty,
    frozenset_new,
    set_len,
    set_new,
    set_pop,
    set_size,
    set_update,
)

from _bench_util import BenchSession

S_SMALL = {10, 20, 30, 40}
S_MID = set(range(64))
FS_SMALL = frozenset(S_SMALL)
HIT = 20
MISS = -1
UPD = [1, 2, 3]


def py_scontains(s: object, value: object) -> bool:
    return value in s  # type: ignore[operator]


def py_slen(s: set) -> int:
    return len(s)


def py_ssize(s: object) -> int:
    return len(s)  # type: ignore[arg-type]


def py_scheck(p: object) -> bool:
    return isinstance(p, set)


def py_scheck_exact(p: object) -> bool:
    return type(p) is set


def py_sany_check(p: object) -> bool:
    return isinstance(p, (set, frozenset))


def py_sany_check_exact(p: object) -> bool:
    return type(p) is set or type(p) is frozenset


def py_sfrozen_check(p: object) -> bool:
    return isinstance(p, frozenset)


def py_sfrozen_check_exact(p: object) -> bool:
    return type(p) is frozenset


def py_sempty() -> set:
    return set()


def py_snew(iterable: object) -> set:
    return set(iterable)  # type: ignore[arg-type]


def py_sfrozen_empty() -> frozenset:
    return frozenset()


def py_sfrozen_new(iterable: object) -> frozenset:
    return frozenset(iterable)  # type: ignore[arg-type]


def py_scopy(s: set) -> set:
    return s.copy()


def main() -> None:
    session = BenchSession("cyset — public helpers vs plain Python (tier A)")
    session.header()

    session.section("set_contains  [primary: hit small]")
    session.compare("set_contains", set_contains, py_scontains, S_SMALL, HIT, param="hit small")
    session.compare("set_contains", set_contains, py_scontains, S_SMALL, MISS, param="miss small")
    session.compare("set_contains", set_contains, py_scontains, S_MID, 32, param="hit n=64")
    session.compare("set_contains", set_contains, py_scontains, S_MID, MISS, param="miss n=64")
    session.compare("set_contains", set_contains, py_scontains, FS_SMALL, HIT, param="frozenset hit")

    session.section("set_len / set_size / checks / constructors")
    session.compare("set_len", set_len, py_slen, S_SMALL, param="small")
    session.compare("set_len", set_len, py_slen, S_MID, param="n=64")
    session.compare("set_size", set_size, py_ssize, S_SMALL, param="set")
    session.compare("set_size", set_size, py_ssize, FS_SMALL, param="frozenset")
    session.compare("set_check", set_check, py_scheck, S_SMALL, param="set")
    session.compare("set_check_exact", set_check_exact, py_scheck_exact, S_SMALL, param="exact")
    session.compare("set_any_check", set_any_check, py_sany_check, FS_SMALL, param="frozenset")
    session.compare("set_any_check_exact", set_any_check_exact, py_sany_check_exact, FS_SMALL, param="exact")
    session.compare("frozenset_check", frozenset_check, py_sfrozen_check, FS_SMALL, param="frozenset")
    session.compare(
        "frozenset_check_exact",
        frozenset_check_exact,
        py_sfrozen_check_exact,
        FS_SMALL,
        param="exact",
    )
    session.compare("set_empty", set_empty, py_sempty, param="empty")
    session.compare("frozenset_empty", frozenset_empty, py_sfrozen_empty, param="empty")
    session.compare("set_new", set_new, py_snew, [1, 2, 3], param="list3")
    session.compare("frozenset_new", frozenset_new, py_sfrozen_new, [1, 2, 3], param="list3")
    session.compare("set_copy", set_copy, py_scopy, S_SMALL, param="small")
    session.compare("set_copy", set_copy, py_scopy, S_MID, param="n=64")

    session.section("mutators (fresh set each call)")

    def c_sadd() -> int:
        return set_add({1, 2}, 3)

    def b_sadd() -> int:
        s = {1, 2}
        s.add(3)
        return 0

    def c_sdiscard_hit() -> int:
        return set_discard({1, 2, 3}, 2)

    def b_sdiscard_hit() -> int:
        s = {1, 2, 3}
        s.discard(2)
        return 1

    def c_sdiscard_miss() -> int:
        return set_discard({1, 2, 3}, 9)

    def b_sdiscard_miss() -> int:
        s = {1, 2, 3}
        s.discard(9)
        return 0

    def c_spop() -> object:
        return set_pop({1, 2, 3})

    def b_spop() -> object:
        return {1, 2, 3}.pop()

    def c_sclear() -> int:
        return set_clear({1, 2, 3})

    def b_sclear() -> int:
        s = {1, 2, 3}
        s.clear()
        return 0

    def c_supdate() -> int:
        return set_update({1}, UPD)

    def b_supdate() -> int:
        s = {1}
        s.update(UPD)
        return 0

    session.compare("set_add", c_sadd, b_sadd, param="add")
    session.compare("set_discard", c_sdiscard_hit, b_sdiscard_hit, param="hit")
    session.compare("set_discard", c_sdiscard_miss, b_sdiscard_miss, param="miss")
    session.compare("set_pop", c_spop, b_spop, param="n=3")
    session.compare("set_clear", c_sclear, b_sclear, param="n=3")
    session.compare("set_update", c_supdate, b_supdate, param="list3")

    session.summary()


if __name__ == "__main__":
    main()
