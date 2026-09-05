"""Compare public :mod:`cypy` cyansi helpers vs plain Python (tier A).

Depth: table hit vs miss codes, strip with/without CSI, ansi_wrap.
Run: python bench/cyansi_bench.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import ansi_bg8, ansi_bold, ansi_fg8, ansi_fg256, ansi_reset, ansi_strip, ansi_wrap

from _bench_util import BenchSession

_CSI = re.compile(r"\x1b\[[0-9;]*[ -/]*[@-~]")
_RESET = "\x1b[0m"


def py_reset() -> str:
    return _RESET


def py_fg8(code: int) -> str:
    return f"\x1b[{code}m"


def py_bg8(code: int) -> str:
    return f"\x1b[{code}m"


def py_fg256(n: int) -> str:
    return f"\x1b[38;5;{n}m"


def py_bold(on: bool = True) -> str:
    return "\x1b[1m" if on else _RESET


def py_wrap(prefix: str, text: str, suffix: str | None = None) -> str:
    if suffix is None:
        suffix = _RESET
    return prefix + text + suffix


def py_strip(s: str) -> str:
    return _CSI.sub("", s)


COLORED = f"\x1b[31mhello\x1b[0m world \x1b[38;5;42mx\x1b[0m"
PLAIN = "hello world plain text without escapes"


def main() -> None:
    session = BenchSession("cyansi — public helpers vs plain Python (tier A)")
    session.header()

    # Warm intern tables once outside timed loop bias.
    ansi_reset()
    ansi_fg8(31)
    ansi_fg256(42)

    session.section("SGR builders  [primary: ansi_fg8 table hit]")
    session.compare("ansi_fg8", ansi_fg8, py_fg8, 31, param="table hit")
    session.compare("ansi_fg8", ansi_fg8, py_fg8, 91, param="miss fmt")
    session.compare("ansi_bg8", ansi_bg8, py_bg8, 41, param="table hit")
    session.compare("ansi_fg256", ansi_fg256, py_fg256, 42, param="table hit")
    session.compare("ansi_fg256", ansi_fg256, py_fg256, 300, param="miss fmt")
    session.compare("ansi_bold", ansi_bold, py_bold, True, param="on")
    session.compare("ansi_reset", ansi_reset, py_reset, param="ansi_reset")
    session.compare("ansi_wrap", ansi_wrap, py_wrap, "\x1b[31m", "hi", param="ansi_wrap")

    session.section("ansi_strip")
    session.compare("ansi_strip", ansi_strip, py_strip, COLORED, param="with CSI")
    session.compare("ansi_strip", ansi_strip, py_strip, PLAIN, param="no CSI")

    session.summary()


if __name__ == "__main__":
    main()
