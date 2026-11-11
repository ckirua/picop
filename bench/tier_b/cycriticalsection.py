"""Tier B: cycriticalsection helpers against natural Cython baselines.

Run: bash bench/tier_b/run.sh cycriticalsection
"""
from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session


def main() -> None:
    tb = ensure_ext("cycriticalsection")
    session = tier_b_session("cycriticalsection — Tier B")
    session.header()
    print(f"inner loop N={N:,}")
    print()

    session.section("object critical section around dict update")
    session.compare("cs_begin / cs_end", tb.cypy_object_section,
                    tb.baseline_object_section, {"value": 0}, N,
                    param="vs with cython.critical_section(d)")

    session.section("custom mutex critical section around counter update")
    session.compare("cs_begin_mutex / cs_end", tb.cypy_mutex_counter,
                    tb.baseline_mutex_counter, N, param="vs mutex_lock / mutex_unlock")

    session.section("two custom mutexes around two-dict swap")
    session.compare("cs2_begin_mutex / cs2_end", tb.cypy_two_mutex_swap,
                    tb.baseline_two_mutex_swap, {"value": 1}, {"value": 2}, N,
                    param="vs two sequential lock/unlock pairs")

    session.section("runtime critical-sections-enabled check in hot loop")
    session.compare("critical_sections_enabled()", tb.cypy_enabled_check,
                    tb.baseline_enabled_check, N,
                    param="vs sys._is_gil_enabled()")

    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
