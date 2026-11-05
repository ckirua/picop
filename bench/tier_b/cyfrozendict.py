"""Tier B: frozendict helpers vs Cython baselines."""
from __future__ import annotations

import builtins

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session


def main() -> None:
    if not hasattr(builtins, "frozendict"):
        print("n/a — frozendict is a CPython 3.15+ type")
        return

    frozendict = builtins.frozendict
    tb = ensure_ext("cyfrozendict")
    frozen = frozendict({"key": 1})
    plain = {"key": 1}

    session = tier_b_session("cyfrozendict — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("frozendict_check")
    session.compare("frozendict_check", tb.cypy_frozendict_check, tb.baseline_frozendict_check, frozen, N, param="hit")
    session.compare("frozendict_check", tb.cypy_frozendict_check, tb.baseline_frozendict_check, plain, N, param="dict miss")
    session.section("frozendict_check_exact")
    session.compare("frozendict_check_exact", tb.cypy_frozendict_check_exact, tb.baseline_frozendict_check_exact, frozen, N, param="hit")
    session.section("anydict_check")
    session.compare("anydict_check", tb.cypy_anydict_check, tb.baseline_anydict_check, plain, N, param="dict")
    session.compare("anydict_check", tb.cypy_anydict_check, tb.baseline_anydict_check, frozen, N, param="frozendict")
    session.section("anydict_check_exact")
    session.compare("anydict_check_exact", tb.cypy_anydict_check_exact, tb.baseline_anydict_check_exact, frozen, N, param="frozendict")
    session.compare("anydict_check_exact", tb.cypy_anydict_check_exact, tb.baseline_anydict_check_exact, plain, N, param="dict")
    session.section("anydict_len")
    session.compare("anydict_len", tb.cypy_anydict_len, tb.baseline_anydict_len, frozen, N, param="frozendict")
    session.compare("anydict_len", tb.cypy_anydict_len, tb.baseline_anydict_len, plain, N, param="dict")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()


if __name__ == "__main__":
    main()
