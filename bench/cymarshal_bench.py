"""Tier A benches for cymarshal."""
from __future__ import annotations
import sys, marshal
from pathlib import Path
_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path: sys.path.insert(0, str(_BENCH_ROOT))
from cypy import marshal_dumps, marshal_loads
from _bench_util import BenchSession

def main():
    session = BenchSession("cymarshal — tier A")
    session.header()
    obj = {"a": 1, "b": [1, 2, 3]}
    blob = marshal.dumps(obj)
    session.section("marshal")
    session.compare("marshal_dumps", marshal_dumps, marshal.dumps, obj, param="dict")
    session.compare("marshal_loads", marshal_loads, marshal.loads, blob, param="dict")
    session.summary()
if __name__ == '__main__':
    main()
