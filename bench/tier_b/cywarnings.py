"""Tier B: warning helper vs warnings.warn in typed Cython loops."""
from __future__ import annotations
import warnings
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session

def main():
    tb = ensure_ext("cywarnings")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        session = tier_b_session("cywarnings — Tier B")
        session.header()
        print(f"inner loop N={N:,}\n")
        session.section("ignored warnings in typed Cython loop")
        session.compare("warn_ex", tb.cypy, tb.baseline, RuntimeWarning, "ignored", N)
        session.summary()
        print("Markdown (paste under ### Tier B):")
        print(markdown_table(session._rows))

if __name__ == "__main__":
    main()
