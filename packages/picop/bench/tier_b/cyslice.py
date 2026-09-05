"""Tier B: cyslice vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = slice(1, 3)

def main() -> None:
    tb = ensure_ext("cyslice")
    session = tier_b_session("cyslice — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("slice_check  [primary]")
    session.compare("slice_check", tb.cypy_slcheck, tb.baseline_slcheck, PAYLOAD, N, param="hit")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
