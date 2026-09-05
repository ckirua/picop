"""Compare public :mod:`cypy` cydict helpers vs plain Python (tier A).

Includes depth cases: miss, stored None, size shapes.
Run: python bench/cydict_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import MappingProxyType

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    dict_check,
    dict_check_exact,
    dict_clear,
    dict_contains,
    dict_copy,
    dict_del,
    dict_get,
    dict_get_ref,
    dict_get_with_error,
    dict_len,
    dict_merge,
    dict_merge_from_seq2,
    dict_new,
    dict_pop,
    dict_proxy,
    dict_set,
    dict_setdefault,
    dict_setdefault_ref,
    dict_size,
    dict_update,
)

from _bench_util import BenchSession

# Primary payload: small dict, interned-like str key hit
D_HIT = {"symbol": "AAPL", "qty": 10, "side": "buy"}
KEY = "symbol"
KEY_MISS = "missing"
D_NONE = {"symbol": None}
D_LARGE = {f"k{i}": i for i in range(256)}
OTHER = {"x": 1, "y": 2}
PAIRS = [("a", 1), ("b", 2)]


def py_dget(d: dict, key: str) -> object:
    return d.get(key)


def py_dget_ref(d: dict, key: object) -> object:
    return d.get(key)


def py_dcontains(d: dict, key: str) -> bool:
    return key in d


def py_dlen(d: dict) -> int:
    return len(d)


def py_dsize(d: object) -> int:
    return len(d)  # type: ignore[arg-type]


def py_dcheck(p: object) -> bool:
    return isinstance(p, dict)


def py_dcheck_exact(p: object) -> bool:
    return type(p) is dict


def py_dnew() -> dict:
    return {}


def py_dproxy(d: dict) -> object:
    return MappingProxyType(d)


def py_dset(d: dict, key: str, value: object) -> int:
    d[key] = value
    return 0


def py_ddel(d: dict, key: str) -> int:
    del d[key]
    return 0


def py_dpop(d: dict, key: str) -> object:
    return d.pop(key, None)


def py_dupdate(d: dict, other: dict) -> int:
    d.update(other)
    return 0


def py_dmerge(d: dict, other: object, override: bool = True) -> int:
    if override:
        d.update(other)  # type: ignore[arg-type]
    else:
        for k, v in other.items():  # type: ignore[union-attr]
            d.setdefault(k, v)
    return 0


def py_dmerge_from_seq2(d: dict, seq2: object, override: bool = True) -> int:
    if override:
        d.update(seq2)  # type: ignore[arg-type]
    else:
        for k, v in seq2:  # type: ignore[union-attr]
            d.setdefault(k, v)
    return 0


def py_dsetdefault(d: dict, key: str, default: object = None) -> object:
    return d.setdefault(key, default)


def py_dsetdefault_ref(d: dict, key: object, default: object = None) -> object:
    return d.setdefault(key, default)


def py_dclear(d: dict) -> None:
    d.clear()


def py_dcopy(d: dict) -> dict:
    return d.copy()


def main() -> None:
    session = BenchSession("cydict — public helpers vs plain Python (tier A)")
    session.header()

    session.section("dict_get vs dict.get  [primary: hit key='symbol']")
    session.compare("dict_get", dict_get, py_dget, D_HIT, KEY, param="hit")
    session.compare("dict_get", dict_get, py_dget, D_HIT, KEY_MISS, param="miss")
    session.compare("dict_get", dict_get, py_dget, D_NONE, KEY, param="stored None")

    session.section("dict_get_ref / dict_get_with_error vs dict.get")
    session.compare("dict_get_ref", dict_get_ref, py_dget_ref, D_HIT, KEY, param="hit")
    session.compare("dict_get_ref", dict_get_ref, py_dget_ref, D_NONE, KEY, param="stored None")
    session.compare(
        "dict_get_with_error",
        dict_get_with_error,
        py_dget_ref,
        D_HIT,
        KEY,
        param="hit",
    )

    session.section("dict_contains / dict_len / dict_size")
    session.compare("dict_contains", dict_contains, py_dcontains, D_HIT, KEY, param="hit")
    session.compare("dict_contains", dict_contains, py_dcontains, D_HIT, KEY_MISS, param="miss")
    session.compare("dict_len", dict_len, py_dlen, D_HIT, param="small")
    session.compare("dict_len", dict_len, py_dlen, D_LARGE, param="n=256")
    session.compare("dict_size", dict_size, py_dsize, D_HIT, param="small")

    session.section("dict_check / dict_new / dict_proxy")
    session.compare("dict_check", dict_check, py_dcheck, D_HIT, param="dict")
    session.compare("dict_check_exact", dict_check_exact, py_dcheck_exact, D_HIT, param="exact")
    session.compare("dict_new", dict_new, py_dnew, param="empty")
    session.compare("dict_proxy", dict_proxy, py_dproxy, D_HIT, param="proxy")

    session.section("mutators (fresh dict each call via wrapper)")

    def cypy_dset() -> int:
        d = {"a": 1}
        return dict_set(d, "b", 2)

    def base_dset() -> int:
        d = {"a": 1}
        return py_dset(d, "b", 2)

    def cypy_ddel() -> int:
        d = {"a": 1, "b": 2}
        return dict_del(d, "b")

    def base_ddel() -> int:
        d = {"a": 1, "b": 2}
        return py_ddel(d, "b")

    def cypy_dpop() -> object:
        d = {"a": 1, "b": 2}
        return dict_pop(d, "b")

    def base_dpop() -> object:
        d = {"a": 1, "b": 2}
        return py_dpop(d, "b")

    def cypy_dupdate() -> int:
        d = {"a": 1}
        return dict_update(d, OTHER)

    def base_dupdate() -> int:
        d = {"a": 1}
        return py_dupdate(d, OTHER)

    def cypy_dmerge() -> int:
        d = {"a": 1}
        return dict_merge(d, OTHER, True)

    def base_dmerge() -> int:
        d = {"a": 1}
        return py_dmerge(d, OTHER, True)

    def cypy_dmerge_seq() -> int:
        d = {"a": 1}
        return dict_merge_from_seq2(d, PAIRS, True)

    def base_dmerge_seq() -> int:
        d = {"a": 1}
        return py_dmerge_from_seq2(d, PAIRS, True)

    def cypy_dsetdefault() -> object:
        d = {"a": 1}
        return dict_setdefault(d, "b", 0)

    def base_dsetdefault() -> object:
        d = {"a": 1}
        return py_dsetdefault(d, "b", 0)

    def cypy_dsetdefault_ref() -> object:
        d = {"a": 1}
        return dict_setdefault_ref(d, "b", 0)

    def base_dsetdefault_ref() -> object:
        d = {"a": 1}
        return py_dsetdefault_ref(d, "b", 0)

    def cypy_dclear() -> None:
        d = {"a": 1}
        dict_clear(d)

    def base_dclear() -> None:
        d = {"a": 1}
        py_dclear(d)

    def cypy_dcopy() -> dict:
        return dict_copy(D_HIT)

    def base_dcopy() -> dict:
        return py_dcopy(D_HIT)

    session.compare("dict_set", cypy_dset, base_dset, param="insert")
    session.compare("dict_del", cypy_ddel, base_ddel, param="delete")
    session.compare("dict_pop", cypy_dpop, base_dpop, param="pop hit")
    session.compare("dict_update", cypy_dupdate, base_dupdate, param="update")
    session.compare("dict_merge", cypy_dmerge, base_dmerge, param="merge override")
    session.compare("dict_merge_from_seq2", cypy_dmerge_seq, base_dmerge_seq, param="pairs")
    session.compare("dict_setdefault", cypy_dsetdefault, base_dsetdefault, param="miss insert")
    session.compare(
        "dict_setdefault_ref",
        cypy_dsetdefault_ref,
        base_dsetdefault_ref,
        param="miss insert",
    )
    session.compare("dict_clear", cypy_dclear, base_dclear, param="clear")
    session.compare("dict_copy", cypy_dcopy, base_dcopy, param="small")

    session.summary()


if __name__ == "__main__":
    main()
