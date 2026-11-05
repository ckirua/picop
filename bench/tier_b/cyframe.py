"""Tier B: frame helpers vs typed Cython attribute baselines."""
from __future__ import annotations

import sys
from pathlib import Path

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session


def _frame():
    return sys._getframe()


def main() -> None:
    tb = ensure_ext("cyframe")
    frame = _frame()
    session = tier_b_session("cyframe — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    for label, cypy, baseline in (
        ("frame_check", tb.cypy_frame_check, tb.baseline_frame_check),
        ("frame_lineno", tb.cypy_frame_lineno, tb.baseline_frame_lineno),
        ("frame_code", tb.cypy_frame_code, tb.baseline_frame_code),
        ("frame_back", tb.cypy_frame_back, tb.baseline_frame_back),
    ):
        session.section(label)
        session.compare(label, cypy, baseline, frame, N)
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()


if __name__ == "__main__":
    main()
