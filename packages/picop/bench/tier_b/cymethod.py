"""Tier B: cymethod vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
class _T:
    def m(self):
        return None

PAYLOAD = _T().m

def main() -> None:
    tb = ensure_ext("cymethod")
    session = tier_b_session("cymethod — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("method_check  [primary]")
    session.compare("method_check", tb.cypy_method_check, tb.baseline_method_check, PAYLOAD, N, param="bound")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
