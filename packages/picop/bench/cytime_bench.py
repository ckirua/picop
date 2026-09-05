"""Tier A benches for cytime."""
from __future__ import annotations
import sys, time
from pathlib import Path
_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path: sys.path.insert(0, str(_BENCH_ROOT))
from cypy import time_monotonic, time_perf_counter, time_wall
from _bench_util import BenchSession

def main():
    session = BenchSession("cytime — tier A")
    session.header()
    session.section("time")
    session.compare("time_wall", time_wall, time.time, param="wall")
    session.compare("time_monotonic", time_monotonic, time.monotonic, param="mono")
    session.compare("time_perf_counter", time_perf_counter, time.perf_counter, param="perf")
    session.summary()
if __name__ == '__main__':
    main()
