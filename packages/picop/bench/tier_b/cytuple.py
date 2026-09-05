"""Tier B: cytuple public helpers vs typed Cython ``cdef`` loops.

Run from repo root::

    python -m bench.tier_b.build cytuple
    python -m bench.tier_b.cytuple
"""

from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session

PAYLOAD: tuple[str, str, str, str] = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT")


def main() -> None:
    ensure_ext("cytuple")
    import cytuple_tb as tb

    session = tier_b_session(
        "cytuple — Tier B (cypy vs typed Cython cdef loop)"
    )
    session.header()
    print(f"inner loop N={N:,}  ·  ratio = cypy_loop / cython_baseline_loop")
    print()

    session.section("tuple_get vs typed t[i]  [primary: index=0]")
    session.compare(
        "tuple_get",
        tb.cypy_tget,
        tb.baseline_tget,
        PAYLOAD,
        0,
        N,
        param="index=0",
    )
    session.compare(
        "tuple_get",
        tb.cypy_tget,
        tb.baseline_tget,
        PAYLOAD,
        2,
        N,
        param="index=2",
    )

    session.section("tuple_get_checked vs typed t[i]")
    session.compare(
        "tuple_get_checked",
        tb.cypy_tget_checked,
        tb.baseline_tget_checked,
        PAYLOAD,
        0,
        N,
        param="index=0",
    )

    session.section("tuple_len / tuple_size vs len(t)")
    session.compare("tuple_len", tb.cypy_tlen, tb.baseline_tlen, PAYLOAD, N, param="vs len")
    session.compare("tuple_size", tb.cypy_tsize, tb.baseline_tlen, PAYLOAD, N, param="vs len")

    session.section("tuple_check / tuple_check_exact")
    session.compare(
        "tuple_check",
        tb.cypy_tcheck,
        tb.baseline_tcheck,
        PAYLOAD,
        N,
        param="tuple",
    )
    session.compare(
        "tuple_check_exact",
        tb.cypy_tcheck_exact,
        tb.baseline_tcheck_exact,
        PAYLOAD,
        N,
        param="tuple",
    )

    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
