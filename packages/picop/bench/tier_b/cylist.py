"""Tier B: cylist public helpers vs typed Cython ``cdef`` loops.

Run::

    python -m bench.tier_b.build cylist
    python -m bench.tier_b.cylist
"""

from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]

def main() -> None:
    tb = ensure_ext("cylist")
    session = tier_b_session("cylist — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("list_get vs l[i]  [primary]")
    session.compare("list_get", tb.cypy_lget, tb.baseline_lget, PAYLOAD, 0, N, param="index=0")
    session.compare("list_get_checked", tb.cypy_lget_checked, tb.baseline_lget, PAYLOAD, 0, N, param="index=0")
    session.section("list_len / list_check")
    session.compare("list_len", tb.cypy_llen, tb.baseline_llen, PAYLOAD, N, param="n=4")
    session.compare("list_check", tb.cypy_lcheck, tb.baseline_lcheck, PAYLOAD, N, param="list")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
