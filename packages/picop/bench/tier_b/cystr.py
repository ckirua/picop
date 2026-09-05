"""Tier B: cystr public helpers vs typed Cython ``cdef`` loops.

Run::

    python -m bench.tier_b.build cystr
    python -m bench.tier_b.cystr
"""

from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
HAY = "abcabc"
NEEDLE = "ab"

def main() -> None:
    tb = ensure_ext("cystr")
    session = tier_b_session("cystr — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("str_contains vs `in`  [primary]")
    session.compare("str_contains", tb.cypy_contains, tb.baseline_contains, HAY, NEEDLE, N, param="short hit")
    session.section("str_eq / str_len / str_check_exact")
    session.compare("str_eq", tb.cypy_streq, tb.baseline_streq, HAY, HAY, N, param="equal")
    session.compare("str_len", tb.cypy_strlen, tb.baseline_strlen, HAY, N, param="short")
    session.compare("str_check_exact", tb.cypy_is_str, tb.baseline_is_str, HAY, N, param="str")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
