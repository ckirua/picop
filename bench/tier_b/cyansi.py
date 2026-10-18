"""Tier B: cyansi public helpers vs typed Cython ``cdef`` loops.

Run::

    python -m bench.tier_b.build cyansi
    python -m bench.tier_b.cyansi
"""

from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
# f-string baseline allocates; keep signal without multi-second runs
N = min(N, 200_000)

def main() -> None:
    tb = ensure_ext("cyansi")
    session = tier_b_session("cyansi — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("ansi_fg8 vs f-string  [primary]")
    session.compare("ansi_fg8", tb.cypy_fg8, tb.baseline_fg8, 31, N, param="table hit 31")
    session.compare("ansi_bg8", tb.cypy_bg8, tb.baseline_bg8, 41, N, param="table hit 41")
    session.compare("ansi_bold", tb.cypy_bold, tb.baseline_bold, True, N, param="on")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
