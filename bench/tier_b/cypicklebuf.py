"""Tier B: PickleBuffer creation versus typed memoryview creation."""
from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session


def main() -> None:
    tb = ensure_ext("cypicklebuf")
    obj = bytearray(b"pickle buffer payload")
    session = tier_b_session("cypicklebuf — Tier B")
    session.header()
    print(f"inner loop N={N:,}\n")
    session.section("PickleBuffer creation vs memoryview creation")
    session.compare("pickle_buffer_from_object", tb.cypy_from_object, tb.baseline_from_object, obj, N)
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))


if __name__ == "__main__":
    main()
