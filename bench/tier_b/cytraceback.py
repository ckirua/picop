"""Tier B: traceback helpers vs typed Cython attribute baselines."""
from __future__ import annotations

import sys

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session


def _traceback():
    def leaf():
        raise ValueError("benchmark traceback")

    def mid():
        leaf()

    def top():
        mid()

    try:
        top()
    except ValueError:
        return sys.exc_info()[2]
    raise AssertionError("unreachable")


def main() -> None:
    tb = ensure_ext("cytraceback")
    trace = _traceback()
    session = tier_b_session("cytraceback — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    for name in ("check", "next", "frame", "lineno", "lasti", "depth"):
        session.section(f"tb_{name}")
        session.compare(f"tb_{name}", getattr(tb, f"cypy_tb_{name}"), getattr(tb, f"baseline_tb_{name}"), trace, N)
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()


if __name__ == "__main__":
    main()
