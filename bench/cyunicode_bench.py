"""Compare public :mod:`picop` cyunicode helpers vs plain Python (tier A).

Depth: short/long ASCII, non-ASCII UTF-8, already-interned vs fresh.
Run: python bench/cyunicode_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from picop import UnicodeWriter, uintern, uutf8_bytes

from _bench_util import BenchSession, N

SHORT = "hello"
MID = "a" * 64
LONG = "x" * 4096
NON_ASCII = "café résumé 日本語"
FRESH_PREFIX = "cypy-intern-probe-"

# Incremental-builder scenario: one full build over this many short parts is
# the unit of work, so the timed loop counts builds, not parts.
PART = "ab"
PART_COUNT = 80_000
PARTS = tuple(PART for _ in range(PART_COUNT))
BUILD_SAMPLES = 20


def writer_build(parts: tuple[str, ...]) -> str:
    """Plain-Python builder on the public picop.UnicodeWriter (no cdef)."""
    writer = UnicodeWriter(len(parts) * len(PART))
    for part in parts:
        writer.write(part)
    return writer.finish()


def writer_build_no_hint(parts: tuple[str, ...]) -> str:
    """Same, letting the writer grow on its own."""
    writer = UnicodeWriter()
    for part in parts:
        writer.write(part)
    return writer.finish()


def join_build(parts: tuple[str, ...]) -> str:
    return "".join(parts)


def iadd_build(parts: tuple[str, ...]) -> str:
    out = ""
    for part in parts:
        out += part
    return out


def main() -> None:
    session = BenchSession("cyunicode — public helpers vs plain Python (tier A)")
    session.header()

    session.section("uutf8_bytes  [primary: short ASCII]")
    session.compare("uutf8_bytes", uutf8_bytes, str.encode, SHORT, param="short")
    session.compare("uutf8_bytes", uutf8_bytes, str.encode, MID, param="n=64")
    session.compare("uutf8_bytes", uutf8_bytes, str.encode, LONG, param="n=4k")
    session.compare("uutf8_bytes", uutf8_bytes, str.encode, NON_ASCII, param="non-ascii")

    session.section("uintern")
    already = sys.intern("already-interned-constant")
    session.compare("uintern", uintern, sys.intern, already, param="already")
    session.compare("uintern", uintern, sys.intern, SHORT, param="short")
    session.compare("uintern", uintern, sys.intern, NON_ASCII, param="non-ascii")

    session.section("UnicodeWriter vs ''.join vs += accumulation  [80k short parts per build]")
    expected = PART * PART_COUNT
    assert writer_build(PARTS) == join_build(PARTS) == iadd_build(PARTS) == expected
    # Each sample builds the whole 80k-part string, so the timed loop counts
    # builds instead of the env iteration count (n would be 80k × n otherwise).
    session.n = BUILD_SAMPLES
    session.compare("UnicodeWriter", writer_build, join_build, PARTS, param="hint 160k vs join")
    session.compare("UnicodeWriter", writer_build_no_hint, join_build, PARTS, param="no hint vs join")
    session.compare("UnicodeWriter", writer_build_no_hint, iadd_build, PARTS, param="no hint vs += ")
    session.n = N

    session.summary()


if __name__ == "__main__":
    main()
