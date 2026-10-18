"""Tier A benches for cygenobject."""
from __future__ import annotations
import sys, types
from pathlib import Path
_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path: sys.path.insert(0, str(_BENCH_ROOT))
from cypy import gen_check, gen_check_exact
from _bench_util import BenchSession

def _g():
    yield 1

def main():
    session = BenchSession("cygenobject — tier A")
    session.header()
    g = _g()
    session.section("gen_check")
    session.compare("gen_check", gen_check, lambda o: isinstance(o, types.GeneratorType), g, param="gen")
    session.compare("gen_check", gen_check, lambda o: isinstance(o, types.GeneratorType), [1], param="list")
    session.compare("gen_check_exact", gen_check_exact, lambda o: type(o) is types.GeneratorType, g, param="gen")
    session.summary()
if __name__ == '__main__':
    main()
