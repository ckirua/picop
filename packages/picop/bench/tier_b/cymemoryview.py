"""Tier B: cymemoryview vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = memoryview(b"abc")

def main() -> None:
    tb = ensure_ext("cymemoryview")
    session = tier_b_session("cymemoryview — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("memoryview_check  [primary]")
    session.compare("memoryview_check", tb.cypy_mvcheck, tb.baseline_mvcheck, PAYLOAD, N, param="hit")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
