"""Tier B: cygenobject vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
def _g():
    yield 1
PAYLOAD = _g()

def main() -> None:
    tb = ensure_ext("cygenobject")
    session = tier_b_session("cygenobject — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("gen_check  [primary]")
    session.compare("gen_check", tb.cypy_gen_check, tb.baseline_gen_check, PAYLOAD, N, param="gen")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
