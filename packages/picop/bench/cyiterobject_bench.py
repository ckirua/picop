"""Tier A benches for cyiterobject."""
from __future__ import annotations
import sys
from pathlib import Path
_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path: sys.path.insert(0, str(_BENCH_ROOT))
from cypy import seqiter_check, seqiter_new, calliter_check, calliter_new
from _bench_util import BenchSession

def main():
    session = BenchSession("cyiterobject — tier A")
    session.header()
    si = seqiter_new([1,2,3])
    ci = calliter_new(iter([1]).__next__, object())
    session.section("checks / new")
    session.compare("seqiter_check", seqiter_check, lambda o: type(o).__name__=='iterator', si, param="seqiter")
    session.compare("seqiter_new", seqiter_new, iter, [1,2,3], param="list")
    session.compare("calliter_check", calliter_check, lambda o: type(o).__name__=='callable_iterator', ci, param="calliter")
    session.compare("calliter_new", calliter_new, iter, lambda: 1, 2, param="call")
    session.summary()
if __name__ == '__main__':
    main()
