"""Tier B: cyconversion vs typed Cython cdef loops."""

from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session

PI = b"3.14159"
A = b"AbC"
B = b"aBc"


def main() -> None:
    tb = ensure_ext("cyconversion")
    session = tier_b_session("cyconversion — Tier B")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("conv_cstr_to_double  [primary]")
    session.compare(
        "conv_cstr_to_double",
        tb.cypy_conv_string_to_double,
        tb.baseline_conv_string_to_double,
        PI,
        N,
        param="pi",
    )
    session.section("conv_stricmp")
    session.compare(
        "conv_stricmp",
        tb.cypy_conv_stricmp,
        tb.baseline_conv_stricmp,
        A,
        B,
        N,
        param="icmp",
    )
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
