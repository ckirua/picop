"""Tier B: sentinel helpers vs Cython baselines."""
from __future__ import annotations

import builtins

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session


def main() -> None:
    if not hasattr(builtins, "sentinel"):
        print("n/a — sentinel is a CPython 3.15+ type")
        return

    sentinel = builtins.sentinel
    tb = ensure_ext("cysentinel")
    sample = sentinel("bench_sample")
    other = object()

    session = tier_b_session("cysentinel — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("sentinel_check")
    session.compare("sentinel_check", tb.cypy_sentinel_check, tb.baseline_sentinel_check, sample, N, param="hit")
    session.compare("sentinel_check", tb.cypy_sentinel_check, tb.baseline_sentinel_check, other, N, param="miss")
    session.section("sentinel_check_exact")
    session.compare("sentinel_check_exact", tb.cypy_sentinel_check_exact, tb.baseline_sentinel_check_exact, sample, N, param="hit")
    session.compare("sentinel_check_exact", tb.cypy_sentinel_check_exact, tb.baseline_sentinel_check_exact, other, N, param="miss")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()


if __name__ == "__main__":
    main()
