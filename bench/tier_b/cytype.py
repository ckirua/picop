"""Tier B: cytype vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = int

def main() -> None:
    tb = ensure_ext("cytype")
    session = tier_b_session("cytype — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("type_check  [primary]")
    session.section("type_get_name")
    session.compare("type_get_name", tb.cypy_type_get_name, tb.baseline_type_get_name, PAYLOAD, N)
    session.section("type_get_qualname")
    session.compare("type_get_qualname", tb.cypy_type_get_qualname, tb.baseline_type_get_qualname, PAYLOAD, N)
    session.section("type_get_flags")
    session.compare("type_get_flags", tb.cypy_type_get_flags, tb.baseline_type_get_flags, PAYLOAD, N)
    session.section("type_get_dict")
    session.compare("type_get_dict", tb.cypy_type_get_dict, tb.baseline_type_get_dict, PAYLOAD, N)
    session.compare("type_check", tb.cypy_type_check, tb.baseline_type_check, PAYLOAD, N, param="hit")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
