"""Tier B interpreter-guard comparisons (Order 077)."""

from __future__ import annotations

import sys

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session


def main() -> None:
    ensure_ext("cythread")
    import cythread_tb as tb

    session = tier_b_session("cythread — Tier B (interpreter guards)")
    session.header()
    if sys.version_info < (3, 15):
        print("n/a: interpreter guards require CPython 3.15+ (the fallback IS the GILState pair)")
        session.summary()
        return

    session.section("guard_from_current/guard_close")
    session.compare("guard_from_current/guard_close", tb.cypy_guard_loop, tb.baseline_gil_loop, N, param="per iteration")
    session.section("threadstate_ensure/release")
    session.compare("threadstate_ensure/release", tb.cypy_ensure_loop, tb.baseline_gil_loop, N, param="guard held")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))


if __name__ == "__main__":
    main()
