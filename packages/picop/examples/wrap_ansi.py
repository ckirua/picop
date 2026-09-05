"""Python usage of :mod:`picop` ANSI helpers.

Run: python examples/wrap_ansi.py
"""

from picop import ansi_fg8, ansi_reset, ansi_strip, ansi_wrap
from picop.cyansi import FOREGROUND_COLORS_8

def main() -> None:
    prefix = ansi_fg8(32)
    message = ansi_wrap(prefix, "picop cyansi", ansi_reset())
    print(message)
    print(f"visible text: {ansi_strip(message)!r}")
    print(f"static red: {FOREGROUND_COLORS_8.RED!r}")

if __name__ == "__main__":
    main()
