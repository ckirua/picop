"""Tier B: cyiterator vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = iter([1, 2, 3])

def main() -> None:
    tb = ensure_ext("cyiterator")
    session = tier_b_session("cyiterator — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("iter_check  [primary]")
    session.compare("iter_check", tb.cypy_iter_check, tb.baseline_iter_check, PAYLOAD, N, param="list_iter")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
