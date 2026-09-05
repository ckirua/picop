"""Tier B: cydatetime vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
from datetime import date
PAYLOAD = date(2026, 7, 21)

def main() -> None:
    tb = ensure_ext("cydatetime")
    session = tier_b_session("cydatetime — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("dt_date_check  [primary]")
    session.compare("dt_date_check", tb.cypy_dt_date_check, tb.baseline_dt_date_check, PAYLOAD, N, param="date")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
