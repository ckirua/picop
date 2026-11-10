"""Tier A benches for cydescr."""
from __future__ import annotations
import sys
from pathlib import Path
_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path: sys.path.insert(0, str(_BENCH_ROOT))
from picop import descr_is_data, descr_name, descr_objclass
from _bench_util import BenchSession

class P:
    @property
    def x(self): return 1
    def m(self): return 1

def main():
    session = BenchSession("cydescr — tier A")
    session.header()
    prop = P.x
    meth = P.m
    session.section("descr_is_data")
    meth = str.upper
    session.section("descriptor metadata")
    session.compare("descr_is_data", descr_is_data, lambda d: hasattr(type(d), '__set__') or hasattr(type(d), '__delete__'), prop, param="property")
    session.compare("descr_name", descr_name, lambda d: d.__name__, meth, param="method descriptor")
    session.compare("descr_objclass", descr_objclass, lambda d: str, meth, param="method descriptor")
    session.summary()
if __name__ == '__main__':
    main()
