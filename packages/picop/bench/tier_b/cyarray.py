"""Tier B: cyarray public helpers vs typed Cython ``cdef`` loops.

Run::

    python -m bench.tier_b.build cyarray
    python -m bench.tier_b.cyarray
"""

from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
from array import array

PAYLOAD = array("i", range(8))

def main() -> None:
    tb = ensure_ext("cyarray")
    session = tier_b_session("cyarray — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("array_len vs len  [primary]")
    session.compare("array_len", tb.cypy_aylen, tb.baseline_aylen, PAYLOAD, N, param="small i")
    session.section("array_check")
    session.compare("array_check", tb.cypy_aycheck, tb.baseline_aycheck, PAYLOAD, N, param="array")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
