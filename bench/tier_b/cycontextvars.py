"""Tier B: cycontextvars vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
from contextvars import copy_context
PAYLOAD = copy_context()

def main() -> None:
    tb = ensure_ext("cycontextvars")
    session = tier_b_session("cycontextvars — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("ctx_check_exact  [primary]")
    session.compare("ctx_check_exact", tb.cypy_ctx_check_exact, tb.baseline_ctx_check_exact, PAYLOAD, N, param="Context")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
