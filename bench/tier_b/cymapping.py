"""Tier B: cymapping vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = {"a": 1}

def main() -> None:
    tb = ensure_ext("cymapping")
    session = tier_b_session("cymapping — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("map_check  [primary]")
    session.compare("map_check", tb.cypy_map_check, tb.baseline_map_check, PAYLOAD, N, param="hit")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
