"""Tier B: cyiterobject vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = iter([1, 2, 3])

def main() -> None:
    tb = ensure_ext("cyiterobject")
    session = tier_b_session("cyiterobject — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("seqiter_check  [primary]")
    session.compare("seqiter_check", tb.cypy_seqiter_check, tb.baseline_seqiter_check, PAYLOAD, N, param="list_iter")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
