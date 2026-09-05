"""Tier B: cyweakref vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
from weakref import ref
class _T:
    pass
_OBJ = _T()
PAYLOAD = ref(_OBJ)

def main() -> None:
    tb = ensure_ext("cyweakref")
    session = tier_b_session("cyweakref — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("weakref_check  [primary]")
    session.compare("weakref_check", tb.cypy_weakref_check, tb.baseline_weakref_check, PAYLOAD, N, param="ref")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
