"""Compare public :mod:`cypy` cyunicode helpers vs plain Python (tier A).

Depth: short/long ASCII, non-ASCII UTF-8, already-interned vs fresh.
Run: python bench/cyunicode_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import uintern, uutf8_bytes

from _bench_util import BenchSession

SHORT = "hello"
MID = "a" * 64
LONG = "x" * 4096
NON_ASCII = "café résumé 日本語"
FRESH_PREFIX = "cypy-intern-probe-"


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

    session.summary()


if __name__ == "__main__":
    main()
