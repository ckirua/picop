"""Tier B: cybytearray public helpers vs typed Cython ``cdef`` loops.

Run::

    python -m bench.tier_b.build cybytearray
    python -m bench.tier_b.cybytearray
"""

from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = bytearray(b"abcabc")

def main() -> None:
    tb = ensure_ext("cybytearray")
    session = tier_b_session("cybytearray — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("bytearray_len vs len  [primary]")
    session.compare("bytearray_len", tb.cypy_balen, tb.baseline_balen, PAYLOAD, N, param="small")
    session.section("bytearray_check / exact")
    session.compare("bytearray_check", tb.cypy_bacheck, tb.baseline_bacheck, PAYLOAD, N, param="bytearray")
    session.compare("bytearray_check_exact", tb.cypy_bacheck_exact, tb.baseline_bacheck_exact, PAYLOAD, N, param="bytearray")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
