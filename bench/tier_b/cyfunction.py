"""Tier B: cyfunction vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
def _f():
    return None
PAYLOAD = _f

def main() -> None:
    tb = ensure_ext("cyfunction")
    session = tier_b_session("cyfunction — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("func_check  [primary]")
    session.compare("func_check", tb.cypy_func_check, tb.baseline_func_check, PAYLOAD, N, param="def")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
