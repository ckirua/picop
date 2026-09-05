"""Tier B: cydict public helpers vs typed Cython ``cdef`` loops.

Run::

    python -m bench.tier_b.build cydict
    python -m bench.tier_b.cydict
"""

from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = {"symbol": "BTCUSDT", "price": "1", "qty": "2"}

def main() -> None:
    tb = ensure_ext("cydict")
    session = tier_b_session("cydict — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("dict_get vs dict.get  [primary]")
    session.compare("dict_get", tb.cypy_dget, tb.baseline_dget, PAYLOAD, "symbol", N, param="hit symbol")
    session.section("dict_contains / dict_len / dict_check")
    session.compare("dict_contains", tb.cypy_dcontains, tb.baseline_dcontains, PAYLOAD, "symbol", N, param="hit")
    session.compare("dict_len", tb.cypy_dlen, tb.baseline_dlen, PAYLOAD, N, param="n=3")
    session.compare("dict_check", tb.cypy_dcheck, tb.baseline_dcheck, PAYLOAD, N, param="dict")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
