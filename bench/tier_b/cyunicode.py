"""Tier B: cyunicode public helpers vs typed Cython ``cdef`` loops.

Run::

    python -m bench.tier_b.build cyunicode
    python -m bench.tier_b.cyunicode
"""

from __future__ import annotations

from picop import UnicodeWriter

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
SHORT = "BTCUSDT"
PARTS = tuple(SHORT for _ in range(N))


def python_writer_build(parts: tuple[str, ...]) -> str:
    """Plain-Python UnicodeWriter loop (Tier A-style: public call surface)."""
    writer = UnicodeWriter()
    for part in parts:
        writer.write(part)
    return writer.finish()


def join_build(parts: tuple[str, ...]) -> str:
    return "".join(parts)


def main() -> None:
    tb = ensure_ext("cyunicode")
    session = tier_b_session("cyunicode — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("uutf8_bytes vs AsUTF8String  [primary]")
    session.compare("uutf8_bytes", tb.cypy_uutf8_bytes, tb.baseline_uutf8_bytes, SHORT, N, param="short")
    session.section("uintern vs InternInPlace")
    session.compare("uintern", tb.cypy_uintern, tb.baseline_uintern, SHORT, N, param="already")
    session.section("UnicodeWriter vs join  [Tier A-style: Python loop over N parts]")
    session.compare("UnicodeWriter", python_writer_build, join_build, PARTS, param=f"N={N:,} parts")
    session.section("cypy_writer vs baseline_join  [Tier B]")
    session.compare("UnicodeWriter", tb.cypy_writer, tb.baseline_join, SHORT, N, param=f"N={N:,} parts")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
