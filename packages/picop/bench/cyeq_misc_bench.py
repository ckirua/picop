"""Tier A depth for late identity / misc ``*_eq`` helpers vs ``==``.

Run: python bench/cyeq_misc_bench.py
"""

from __future__ import annotations

import sys
import types
import weakref
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    capsule_eq,
    func_eq,
    gen_eq,
    iter_eq,
    method_eq,
    mod_eq,
    obj_eq,
    weakref_eq,
)

from _bench_util import BenchSession


def _f() -> None:
    return None


def _g() -> None:
    return None


class _C:
    def m(self) -> None:
        return None


def _gen() -> object:
    yield 1


def py_eq(a: object, b: object) -> bool:
    return a == b


def main() -> None:
    session = BenchSession("cyeq_misc — identity/misc *_eq vs ``==`` (tier A)")
    session.header()

    c = _C()
    m1 = c.m
    m2 = c.m
    m_other = _C().m
    mod = sys.modules["sys"]
    g1 = _gen()
    g2 = _gen()
    it1 = iter([1, 2])
    it2 = iter([1, 2])

    session.section("func_eq / method_eq / mod_eq")
    session.compare("func_eq", func_eq, py_eq, _f, _f, param="identity")
    session.compare("func_eq", func_eq, py_eq, _f, _g, param="ne")
    session.compare("method_eq", method_eq, py_eq, m1, m2, param="same bound")
    session.compare("method_eq", method_eq, py_eq, m1, m_other, param="diff self")
    session.compare("mod_eq", mod_eq, py_eq, mod, mod, param="identity")

    session.section("gen_eq / iter_eq / obj_eq")
    session.compare("gen_eq", gen_eq, py_eq, g1, g1, param="identity")
    session.compare("gen_eq", gen_eq, py_eq, g1, g2, param="ne")
    session.compare("iter_eq", iter_eq, py_eq, it1, it1, param="identity")
    session.compare("iter_eq", iter_eq, py_eq, it1, it2, param="ne")
    session.compare("obj_eq", obj_eq, py_eq, 1, 1, param="int eq")
    session.compare("obj_eq", obj_eq, py_eq, float("nan"), float("nan"), param="nan is nan")

    class _Target:
        pass

    tgt = _Target()
    r1 = weakref.ref(tgt)
    r2 = weakref.ref(tgt)
    other = weakref.ref(_Target())
    session.section("weakref_eq / capsule_eq")
    session.compare("weakref_eq", weakref_eq, py_eq, r1, r2, param="same referent")
    session.compare("weakref_eq", weakref_eq, py_eq, r1, r1, param="identity")
    session.compare("weakref_eq", weakref_eq, py_eq, r1, other, param="ne referent")

    # Capsules: identity-only in CPython; build via ctypes PyCapsule_New if needed.
    try:
        import ctypes

        PyCapsule_New = ctypes.pythonapi.PyCapsule_New
        PyCapsule_New.restype = ctypes.py_object
        PyCapsule_New.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p]
        cap_a = PyCapsule_New(ctypes.c_void_p(1), b"cypy.bench", None)
        cap_b = PyCapsule_New(ctypes.c_void_p(1), b"cypy.bench", None)
        session.compare("capsule_eq", capsule_eq, py_eq, cap_a, cap_a, param="identity")
        session.compare("capsule_eq", capsule_eq, py_eq, cap_a, cap_b, param="ne")
    except Exception as exc:  # pragma: no cover
        print(f"capsule_eq skipped: {exc}")

    session.summary()


if __name__ == "__main__":
    main()
