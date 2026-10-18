"""Tier A benches for cyfileobject."""
from __future__ import annotations
import sys, tempfile
from pathlib import Path
_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path: sys.path.insert(0, str(_BENCH_ROOT))
from picop import file_getline
from _bench_util import BenchSession

def main():
    session = BenchSession("cyfileobject — tier A")
    session.header()
    with tempfile.TemporaryFile(mode="w+t") as f:
        # Both timing phases consume one line per invocation, including warmup.
        f.write("line1\nline2\n" * (session.n * (session.runs + session.warmup)))
        f.seek(0)
        session.section("getline")
        session.compare(
            "file_getline",
            file_getline,
            lambda p, n: p.readline().removesuffix("\n") if n < 0 else p.readline(n),
            f,
            -1,
            param="line",
        )
    session.summary()
if __name__ == "__main__":
    main()
