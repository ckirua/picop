"""Tier B: cymodule vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
import sys
PAYLOAD = sys

def main() -> None:
    tb = ensure_ext("cymodule")
    session = tier_b_session("cymodule — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("mod_check  [primary]")
    session.compare("mod_check", tb.cypy_mod_check, tb.baseline_mod_check, PAYLOAD, N, param="sys")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
