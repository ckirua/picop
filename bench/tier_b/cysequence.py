"""Tier B: cysequence vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = [1, 2, 3, 4]

def main() -> None:
    tb = ensure_ext("cysequence")
    session = tier_b_session("cysequence — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("seq_get vs l[i]  [primary]")
    session.compare("seq_get", tb.cypy_sqget, tb.baseline_sqget, PAYLOAD, 0, N, param="list[0]")
    session.compare("seq_len", tb.cypy_sqlen, tb.baseline_sqlen, PAYLOAD, N, param="n=4")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
