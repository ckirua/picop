"""Tier A benches for cymapping."""
from __future__ import annotations
import sys
from pathlib import Path
_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path: sys.path.insert(0, str(_BENCH_ROOT))
from cypy import map_check, map_has_key, map_len, map_keys, map_getitem_cstr
from _bench_util import BenchSession

def main():
    session = BenchSession("cymapping — tier A")
    session.header()
    d={"a":1,"b":2}
    session.section("map")
    session.compare("map_check", map_check, lambda o: hasattr(o,'__getitem__') and not isinstance(o,(str,bytes,list,tuple)), d, param="dict")
    session.compare("map_check", map_check, lambda o: hasattr(o,'__getitem__') and not isinstance(o,(str,bytes,list,tuple)), [1], param="list")
    session.compare("map_len", map_len, len, d, param="dict")
    session.compare("map_has_key", map_has_key, lambda o,k: k in o, d, "a", param="hit")
    session.compare("map_getitem_cstr", map_getitem_cstr, lambda o,k: o[k.decode()], d, b"a", param="a")
    session.compare("map_keys", map_keys, lambda o: list(o.keys()), d, param="keys")
    session.summary()
if __name__ == '__main__':
    main()
