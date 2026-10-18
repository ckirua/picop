"""Tier B: cymarshal vs typed Cython cdef loops."""

from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session

# Allocating dumps — keep N modest
N = min(N, 200_000)
PAYLOAD = {"a": 1, "b": [2, 3]}


def main() -> None:
    tb = ensure_ext("cymarshal")
    session = tier_b_session("cymarshal — Tier B")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("marshal_dumps  [primary]")
    session.compare(
        "marshal_dumps",
        tb.cypy_marshal_dumps,
        tb.baseline_marshal_dumps,
        PAYLOAD,
        N,
        param="dict",
    )
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
