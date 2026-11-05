"""Tier B: code helpers vs typed Cython attribute baselines."""
from __future__ import annotations

from pathlib import Path
import sys

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session


def _code():
    def inner(value):
        return value + 1

    return inner.__code__


def main() -> None:
    tb = ensure_ext("cycode")
    code = _code()
    session = tier_b_session("cycode — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("code_check")
    session.compare("code_check", tb.cypy_code_check, tb.baseline_code_check, code, N)
    session.section("code_name")
    session.compare("code_name", tb.cypy_code_name, tb.baseline_code_name, code, N)
    session.section("code_firstlineno")
    session.compare("code_firstlineno", tb.cypy_code_firstlineno, tb.baseline_code_firstlineno, code, N)
    session.section("code_argcount")
    session.compare("code_argcount", tb.cypy_code_argcount, tb.baseline_code_argcount, code, N)
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()


if __name__ == "__main__":
    main()
