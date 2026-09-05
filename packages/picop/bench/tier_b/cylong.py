"""Tier B: cylong vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = 42

def main() -> None:
    tb = ensure_ext("cylong")
    session = tier_b_session("cylong — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("long_check  [primary]")
    session.compare("long_check", tb.cypy_long_check, tb.baseline_long_check, PAYLOAD, N, param="hit")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
