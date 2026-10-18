"""Tier B: cytime vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
# clock syscall — keep N modest
N = min(N, 100_000)

def main() -> None:
    tb = ensure_ext("cytime")
    session = tier_b_session("cytime — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("time_wall vs time.time  [primary]")
    session.compare("time_wall", tb.cypy_time_time, tb.baseline_time_time, N, param="clock")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
