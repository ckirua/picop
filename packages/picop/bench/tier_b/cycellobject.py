"""Tier B: cycellobject vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
def _outer():
    x = 1
    def _inner():
        return x
    return _inner.__closure__[0]

PAYLOAD = _outer()

def main() -> None:
    tb = ensure_ext("cycellobject")
    session = tier_b_session("cycellobject — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("cell_check  [primary]")
    session.compare("cell_check", tb.cypy_cell_check, tb.baseline_cell_check, PAYLOAD, N, param="cell")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
