"""Tier A benches for cycellobject."""
from __future__ import annotations
import sys, types
from pathlib import Path
_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path: sys.path.insert(0, str(_BENCH_ROOT))
from cypy import cell_check, cell_get, cell_new, cell_set
from _bench_util import BenchSession

def main():
    session = BenchSession("cycellobject — tier A")
    session.header()
    # create a real cell via closure
    def make():
        x = 1
        def inner():
            return x
        return inner.__closure__[0]
    c = make()
    session.section("cell")
    session.compare("cell_check", cell_check, lambda o: isinstance(o, types.CellType), c, param="cell")
    session.compare("cell_check", cell_check, lambda o: isinstance(o, types.CellType), 1, param="int")
    session.compare("cell_get", cell_get, lambda o: o.cell_contents, c, param="contents")
    session.compare("cell_new", cell_new, types.CellType, 7, param="7")
    session.summary()
if __name__ == '__main__':
    main()
