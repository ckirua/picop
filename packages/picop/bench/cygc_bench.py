"""Compare public :mod:`cypy` cygc helpers vs ``gc`` module (tier A).

Depth: is_enabled hot path; enable/disable round-trip; collect is smoke-only
(full GC must not run in the N=80k loop).
Run: python bench/cygc_bench.py
"""

from __future__ import annotations

import gc
import sys
import time
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import gc_collect, gc_disable, gc_enable, gc_is_enabled

from _bench_util import BenchSession


def main() -> None:
    session = BenchSession("cygc — public helpers vs gc module (tier A)")
    session.header()

    session.section("gc_is_enabled  [primary]")
    session.compare("gc_is_enabled", gc_is_enabled, gc.isenabled, param="enabled?")

    session.section("enable / disable (restore after)")
    was = gc.isenabled()
    try:

        def c_dis_en() -> int:
            gc_disable()
            return gc_enable()

        def b_dis_en() -> int:
            gc.disable()
            gc.enable()
            return 1 if gc.isenabled() else 0

        session.compare("gc_disable+enable", c_dis_en, b_dis_en, param="roundtrip")
    finally:
        if was:
            gc.enable()
        else:
            gc.disable()

    session.summary()

    # Smoke + one-shot timing for collect (not in N-loop).
    t0 = time.perf_counter()
    n1 = gc_collect()
    t1 = time.perf_counter()
    n2 = gc.collect()
    t2 = time.perf_counter()
    print(
        f"\ncollect smoke (one-shot): cypy={t1 - t0:.4f}s unreachable={n1}  "
        f"gc.collect={t2 - t1:.4f}s unreachable={n2}"
    )


if __name__ == "__main__":
    main()
