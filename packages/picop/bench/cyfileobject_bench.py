"""Tier A benches for cyfileobject."""
from __future__ import annotations
import sys, tempfile, os
from pathlib import Path
_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path: sys.path.insert(0, str(_BENCH_ROOT))
from cypy import file_write_cstr, file_getline
from _bench_util import BenchSession

def main():
    session = BenchSession("cyfileobject — tier A")
    session.header()
    fd, path = tempfile.mkstemp(); os.close(fd)
    with open(path, "w") as f:
        f.write("line1\nline2\n")
    f = open(path, "r")
    session.section("getline")
    session.compare("file_getline", file_getline, lambda p,n: p.readline() if n<0 else p.readline(n), f, -1, param="line")
    f.close(); os.unlink(path)
    session.summary()
if __name__ == "__main__":
    main()
