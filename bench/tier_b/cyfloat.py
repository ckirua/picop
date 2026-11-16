"""Tier B: cyfloat vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
import struct
PAYLOAD = 1.5

def main() -> None:
    tb = ensure_ext("cyfloat")
    session = tier_b_session("cyfloat — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("float_check  [primary]")
    session.compare("float_check", tb.cypy_float_check, tb.baseline_float_check, PAYLOAD, N, param="hit")
    session.section("float_pack8")
    session.compare("float_pack8", tb.cypy_float_pack8, tb.baseline_struct_pack, PAYLOAD, N, param="little")
    session.section("float_unpack8")
    session.compare("float_unpack8", tb.cypy_float_unpack8, tb.baseline_struct_unpack, struct.pack("<d", PAYLOAD), N, param="little")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
