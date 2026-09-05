"""Tier B inventory: ``*_ne`` / startswith / endswith / contains vs typed Cython.

Run::

    python -m bench.tier_b.build cyne_search
    python -m bench.tier_b.cyne_search

Env: ``CPY_TIERB_N`` (default 2_000_000), ``CPY_BENCH_RUNS`` (default 5).
"""

from __future__ import annotations

from array import array

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session

N_HEAVY = max(50_000, N // 40)


def main() -> None:
    tb = ensure_ext("cyne_search")
    session = tier_b_session(
        "cyne_search — Tier B (*_ne / start/end/contains vs typed Cython)"
    )
    session.header()
    print(f"inner loop N={N:,}  (heavy shapes N_HEAVY={N_HEAVY:,})")
    print()

    short = b"BTCUSDT"
    short_ne = b"BTCUSDX"
    prefix = b"BTC"
    suffix = b"USDT"
    one_k = b"a" * 1024
    one_k_ne = b"a" * 1023 + b"b"

    session.section("bytes_ne / startswith / endswith")
    session.compare(
        "bytes_ne", tb.cypy_bytes_ne, tb.baseline_bytes_ne, short, short_ne, N, param="ne short"
    )
    session.compare(
        "bytes_ne",
        tb.cypy_bytes_ne,
        tb.baseline_bytes_ne,
        one_k,
        one_k_ne,
        N_HEAVY,
        param="ne 1KiB",
    )
    session.compare(
        "bytes_startswith",
        tb.cypy_bytes_startswith,
        tb.baseline_bytes_startswith,
        short,
        prefix,
        N,
        param="hit",
    )
    session.compare(
        "bytes_endswith",
        tb.cypy_bytes_endswith,
        tb.baseline_bytes_endswith,
        short,
        suffix,
        N,
        param="hit",
    )

    ba = bytearray(short)
    ba_ne = bytearray(short_ne)
    session.section("bytearray_ne / bytearray_contains")
    session.compare(
        "bytearray_ne",
        tb.cypy_bytearray_ne,
        tb.baseline_bytearray_ne,
        ba,
        ba_ne,
        N,
        param="ne short",
    )
    session.compare(
        "bytearray_contains",
        tb.cypy_bytearray_contains,
        tb.baseline_bytearray_contains,
        ba,
        prefix,
        N,
        param="hit",
    )

    ay = array("i", [1, 2, 3, 4, 5])
    ay_ne = array("i", [1, 2, 3, 4, 9])
    session.section("array_ne / memoryview_ne")
    session.compare(
        "array_ne", tb.cypy_array_ne, tb.baseline_array_ne, ay, ay_ne, N, param="ne small"
    )
    mv = memoryview(short)
    mv_ne = memoryview(short_ne)
    session.compare(
        "memoryview_ne",
        tb.cypy_memoryview_ne,
        tb.baseline_memoryview_ne,
        mv,
        mv_ne,
        N,
        param="ne short",
    )

    session.summary()
    print("Markdown (paste under ### Tier B — ne/search inventory):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
