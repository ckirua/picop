"""Tier B: cybool vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = True

def main() -> None:
    tb = ensure_ext("cybool")
    session = tier_b_session("cybool — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("bool_check  [primary]")
    session.compare("bool_check", tb.cypy_bool_check, tb.baseline_bool_check, PAYLOAD, N, param="hit")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
