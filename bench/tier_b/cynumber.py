"""Tier B: cynumber vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = 7

def main() -> None:
    tb = ensure_ext("cynumber")
    session = tier_b_session("cynumber — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("num_check  [primary]")
    session.compare("num_check", tb.cypy_num_check, tb.baseline_num_check, PAYLOAD, N, param="hit")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
