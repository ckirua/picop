"""Tier B: str_cmp / ordering / str_check / str_is vs typed Cython."""

from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session


def main() -> None:
    tb = ensure_ext("cystr_order")
    session = tier_b_session("cystr_order — Tier B")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    a, b = "hello", "hallo"
    session.section("str_cmp / ordering / check")
    session.compare("str_cmp", tb.cypy_str_cmp, tb.baseline_str_cmp, a, b, N, param="ne")
    session.compare("str_lt", tb.cypy_str_lt, tb.baseline_str_lt, a, b, N, param="lt")
    session.compare("str_le", tb.cypy_str_le, tb.baseline_str_le, a, a, N, param="le eq")
    session.compare("str_gt", tb.cypy_str_gt, tb.baseline_str_gt, a, b, N, param="gt")
    session.compare("str_ge", tb.cypy_str_ge, tb.baseline_str_ge, a, a, N, param="ge eq")
    session.compare("str_check", tb.cypy_str_check, tb.baseline_str_check, a, N, param="str")
    session.compare("str_is", tb.cypy_str_is, tb.baseline_str_is, a, N, param="exact")
    session.summary()
    print(markdown_table(session._rows))


if __name__ == "__main__":
    main()
