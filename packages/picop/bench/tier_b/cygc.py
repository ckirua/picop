"""Tier B: cygc public helpers vs typed Cython ``cdef`` loops.

Run::

    python -m bench.tier_b.build cygc
    python -m bench.tier_b.cygc
"""

from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
def main() -> None:
    tb = ensure_ext("cygc")
    session = tier_b_session("cygc — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("gc_is_enabled vs PyGC_IsEnabled  [primary]")
    session.compare("gc_is_enabled", tb.cypy_gc_is_enabled, tb.baseline_gc_is_enabled, N, param="flag read")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
