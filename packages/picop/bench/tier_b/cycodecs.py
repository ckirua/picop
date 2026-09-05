"""Tier B: cycodecs vs typed Cython cdef loops."""

from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session

ENC = b"utf-8"


def main() -> None:
    tb = ensure_ext("cycodecs")
    session = tier_b_session("cycodecs — Tier B")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("codec_known  [primary]")
    session.compare(
        "codec_known",
        tb.cypy_codec_known,
        tb.baseline_codec_known,
        ENC,
        N,
        param="utf-8",
    )
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
