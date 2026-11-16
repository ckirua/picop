"""Tier B: cylong vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
PAYLOAD = 42

def main() -> None:
    tb = ensure_ext("cylong")
    assert tb.writer_depth_probes()
    assert tb.depth_probes()
    session = tier_b_session("cylong — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("long_check  [primary]")
    session.compare("long_check", tb.cypy_long_check, tb.baseline_long_check, PAYLOAD, N, param="hit")
    session.section("long_as_int32  [narrow conversion]")
    session.compare(
        "long_as_int32",
        tb.cypy_long_as_int32,
        tb.baseline_long_as_int32,
        PAYLOAD,
        N,
        param="small int",
    )
    session.section("long writer vs typed shift/or baseline")
    for ndigits in (1, 32, 256):
        for negative in (False, True):
            assert tb.cypy_writer(PAYLOAD, 1, ndigits, negative) == tb.baseline_writer(PAYLOAD, 1, ndigits, negative)
        session.compare(
            "long_writer",
            tb.cypy_writer,
            tb.baseline_writer,
            PAYLOAD,
            max(1, N // ndigits),
            ndigits,
            False,
            param=f"{ndigits} limbs",
        )
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
