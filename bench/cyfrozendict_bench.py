"""Compare public :mod:`picop` frozendict helpers with plain Python calls (tier A).

Run: python bench/cyfrozendict_bench.py
"""

from __future__ import annotations

import builtins
import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from picop import (
    anydict_check,
    anydict_check_exact,
    anydict_len,
    frozendict_check,
    frozendict_check_exact,
    frozendict_empty,
    frozendict_new,
)

from _bench_util import BenchSession

ITEMS = {"a": 1, "b": 2, "c": 3, "d": 4}


def py_frozendict_check(obj):
    return isinstance(obj, frozendict)


def py_frozendict_check_exact(obj):
    return type(obj) is frozendict


def py_anydict_check(obj):
    return isinstance(obj, (dict, frozendict))


def py_anydict_check_exact(obj):
    t = type(obj)
    return t is dict or t is frozendict


def py_frozendict_new(obj):
    return frozendict(obj)


def py_frozendict_empty():
    return frozendict()


def py_anydict_len(obj):
    return len(obj)


def main() -> None:
    if getattr(builtins, "frozendict", None) is None:
        print("n/a — frozendict is a CPython 3.15+ type; nothing to measure here.")
        return

    frozen = frozendict(ITEMS)

    session = BenchSession("cyfrozendict — public helpers vs plain Python (tier A)")
    session.header()

    session.section("type gates — frozendict / dict-or-frozendict")
    session.compare("frozendict_check", frozendict_check, py_frozendict_check, frozen, param="frozendict hit")
    session.compare("frozendict_check", frozendict_check, py_frozendict_check, ITEMS, param="dict miss")
    session.compare("frozendict_check_exact", frozendict_check_exact, py_frozendict_check_exact, frozen, param="hit")
    session.compare("anydict_check", anydict_check, py_anydict_check, frozen, param="frozendict")
    session.compare("anydict_check", anydict_check, py_anydict_check, ITEMS, param="dict")
    session.compare("anydict_check_exact", anydict_check_exact, py_anydict_check_exact, frozen, param="frozendict")
    session.compare("anydict_check_exact", anydict_check_exact, py_anydict_check_exact, ITEMS, param="dict")

    session.section("construction — frozendict from a mapping / empty")
    session.compare("frozendict_new", frozendict_new, py_frozendict_new, ITEMS, param="from dict (4 items)")
    session.compare("frozendict_new", frozendict_new, py_frozendict_new, frozen, param="from frozendict")
    session.compare("frozendict_empty", frozendict_empty, py_frozendict_empty, param="no iterable")

    session.section("length — dict or frozendict")
    session.compare("anydict_len", anydict_len, py_anydict_len, frozen, param="frozendict, 4 items")
    session.compare("anydict_len", anydict_len, py_anydict_len, ITEMS, param="dict, 4 items")

    session.summary()


if __name__ == "__main__":
    main()
