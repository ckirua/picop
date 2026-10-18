"""Tier A benches for cydescr."""
from __future__ import annotations
import sys
from pathlib import Path
_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path: sys.path.insert(0, str(_BENCH_ROOT))
from cypy import descr_is_data
from _bench_util import BenchSession

class P:
    @property
    def x(self):
        return 1
    def m(self):
        return 2

def main():
    session = BenchSession("cydescr — tier A")
    session.header()
    prop = P.x
    meth = P.m
    session.section("descr_is_data")
    session.compare("descr_is_data", descr_is_data, lambda d: hasattr(d, '__set__') or hasattr(d, '__delete__'), prop, param="property")
    session.compare("descr_is_data", descr_is_data, lambda d: hasattr(d, '__set__') or hasattr(d, '__delete__'), meth, param="method")
    session.summary()
if __name__ == '__main__':
    main()
