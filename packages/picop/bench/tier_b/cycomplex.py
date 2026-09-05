"""Tier B: cycomplex vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = 1+2j

def main() -> None:
    tb = ensure_ext("cycomplex")
    session = tier_b_session("cycomplex — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("complex_check  [primary]")
    session.compare("complex_check", tb.cypy_complex_check, tb.baseline_complex_check, PAYLOAD, N, param="hit")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
