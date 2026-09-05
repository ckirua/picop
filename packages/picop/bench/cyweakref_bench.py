"""Tier A benches for cyweakref."""
from __future__ import annotations
import sys, weakref
from pathlib import Path
_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path: sys.path.insert(0, str(_BENCH_ROOT))
from cypy import weakref_check, weakref_get_object, weakref_new_ref
from _bench_util import BenchSession

class Box: pass

def main():
    session = BenchSession("cyweakref — tier A")
    session.header()
    b = Box()
    r = weakref.ref(b)
    session.section("weakref")
    session.compare("weakref_check", weakref_check, lambda o: weakref.ref is type(o) or isinstance(o, weakref.ReferenceType), r, param="ref")
    session.compare("weakref_new_ref", weakref_new_ref, weakref.ref, b, None, param="new")
    session.compare("weakref_get_object", weakref_get_object, lambda o: o(), r, param="get")
    session.summary()
if __name__ == '__main__':
    main()
