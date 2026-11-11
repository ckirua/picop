"""Tier B: cydescr vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = str.upper
DATA_PAYLOAD = property()

def main() -> None:
    tb = ensure_ext("cydescr")
    session = tier_b_session("cydescr — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("descriptor name [primary]")
    session.section("descr_is_data [secondary]")
    session.compare("descr_is_data", tb.cypy_descr_is_data, tb.baseline_descr_is_data, DATA_PAYLOAD, N, param="property")
    session.compare("descr_name", tb.cypy_descr_name, tb.baseline_descr_name, PAYLOAD, N, param="method descriptor")
    session.compare("descr_objclass", tb.cypy_descr_objclass, tb.baseline_descr_objclass, PAYLOAD, N, param="method descriptor")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
