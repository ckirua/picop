"""Tier B: cyobject vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = (1, 2, 3, 4)

def main() -> None:
    tb = ensure_ext("cyobject")
    session = tier_b_session("cyobject — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("obj_type / obj_len")
    session.compare("obj_type", tb.cypy_obj_type, tb.baseline_obj_type, "x", N, param="str")
    session.compare("obj_len", tb.cypy_obj_len, tb.baseline_obj_len, PAYLOAD, N, param="tuple")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
