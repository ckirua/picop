"""Tier B: cybuffer vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = bytearray(b"abc")

def main() -> None:
    tb = ensure_ext("cybuffer")
    session = tier_b_session("cybuffer — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("buf_check  [primary]")
    session.compare("buf_check", tb.cypy_buf_check, tb.baseline_buf_check, PAYLOAD, N, param="hit")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
