"""Tier A benches for cycellobject."""
from __future__ import annotations
import sys, types
from pathlib import Path
_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path: sys.path.insert(0, str(_BENCH_ROOT))
from picop.cycellobject import cell_check, cell_get, cell_new, cell_set, cell_swap, cell_empty
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
    old = cell_new(1)
    replacement = object()
    session.compare("cell_swap", cell_swap,
                    lambda cell, value: (cell_get(cell), cell_set(cell, value))[0],
                    old, replacement, param="filled/get+set")
    session.compare("cell_empty", lambda _: cell_empty(), lambda _: cell_new(None), None,
                    param="vs-new-none")
    session.compare("cell_new", cell_new, types.CellType, 7, param="7")
    session.summary()
if __name__ == '__main__':
    main()
