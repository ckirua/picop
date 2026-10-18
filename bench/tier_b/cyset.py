"""Tier B: cyset public helpers vs typed Cython ``cdef`` loops.

Run::

    python -m bench.tier_b.build cyset
    python -m bench.tier_b.cyset
"""

from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = {"BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"}

def main() -> None:
    tb = ensure_ext("cyset")
    session = tier_b_session("cyset — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("set_contains vs `in`  [primary]")
    session.compare("set_contains", tb.cypy_scontains, tb.baseline_scontains, PAYLOAD, "BTCUSDT", N, param="hit")
    session.section("set_len / set_check")
    session.compare("set_len", tb.cypy_slen, tb.baseline_slen, PAYLOAD, N, param="n=4")
    session.compare("set_check", tb.cypy_scheck, tb.baseline_scheck, PAYLOAD, N, param="set")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
