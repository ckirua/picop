"""Compare public :mod:`cypy` cyobject helpers vs plain Python (tier A).

Run: python bench/cyobject_bench.py
"""

from __future__ import annotations

import operator
import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    obj_callable,
    obj_getattr,
    obj_getitem,
    obj_hasattr,
    obj_hash,
    obj_isinstance,
    obj_istrue,
    obj_len,
    obj_richcompare_bool,
    obj_size,
    obj_str,
    obj_type,
)

from _bench_util import BenchSession

EQ = 2  # Py_EQ


def main() -> None:
    session = BenchSession("cyobject — public helpers vs plain Python (tier A)")
    session.header()

    class Box:
        a = 1

    box = Box()
    d = {"a": 1, "b": 2}
    session.section("attr / type  [primary: obj_getattr]")
    session.compare("obj_hasattr", obj_hasattr, hasattr, box, "a", param="hit")
    session.compare("obj_hasattr", obj_hasattr, hasattr, box, "z", param="miss")
    session.compare("obj_getattr", obj_getattr, getattr, box, "a", param="box.a")
    session.compare("obj_type", obj_type, type, d, param="dict")
    session.compare("obj_isinstance", obj_isinstance, isinstance, d, dict, param="dict")
    session.compare("obj_callable", obj_callable, callable, len, param="len")
    session.compare("obj_callable", obj_callable, callable, 3, param="int")

    session.section("truth / hash / len / item")
    session.compare("obj_istrue", obj_istrue, bool, d, param="dict")
    session.compare("obj_istrue", obj_istrue, bool, 0, param="0")
    session.compare("obj_hash", obj_hash, hash, "abc", param="str")
    session.compare("obj_len", obj_len, len, d, param="dict")
    session.compare("obj_size", obj_size, len, d, param="dict")
    session.compare("obj_getitem", obj_getitem, operator.getitem, d, "a", param="d[a]")
    session.compare("obj_str", obj_str, str, 42, param="42")
    session.compare(
        "obj_richcompare_bool",
        obj_richcompare_bool,
        lambda a, b, op: a == b,
        1,
        1,
        EQ,
        param="1==1",
    )

    session.summary()


if __name__ == "__main__":
    main()
