"""Tier B: cybytes public helpers vs typed Cython ``cdef`` loops.

Run::

    python -m bench.tier_b.build cybytes
    python -m bench.tier_b.cybytes
"""

from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
HAY = b"abcabc"
NEEDLE = b"ab"

def main() -> None:
    tb = ensure_ext("cybytes")
    session = tier_b_session("cybytes — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("bytes_contains vs `in`  [primary]")
    session.compare("bytes_contains", tb.cypy_bcontains, tb.baseline_bcontains, HAY, NEEDLE, N, param="small multi hit")
    session.section("bytes_eq vs `==`")
    session.compare("bytes_eq", tb.cypy_beq, tb.baseline_beq, HAY, HAY, N, param="equal")
    session.section("bytes_len / bytes_check")
    session.compare("bytes_len", tb.cypy_blen, tb.baseline_blen, HAY, N, param="small")
    session.compare("bytes_check", tb.cypy_bcheck, tb.baseline_bcheck, HAY, N, param="bytes")
    session.compare("bytes_check_exact", tb.cypy_bcheck_exact, tb.baseline_bcheck_exact, HAY, N, param="bytes")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
