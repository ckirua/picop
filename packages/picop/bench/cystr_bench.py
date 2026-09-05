"""Compare public :mod:`cypy` cystr helpers vs plain Python (tier A).

Depth: ASCII vs non-ASCII kinds, short/long haystack, hit/miss str_contains, prefix/suffix.
Run: python bench/cystr_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy.cystr import (
    str_all_alnum_ascii,
    str_all_alpha_ascii,
    str_all_digits,
    str_as_or_empty,
    str_char_at,
    str_concat,
    str_concat3,
    str_concat4,
    str_contains,
    str_endswith,
    find,
    str_first_char,
    is_ascii,
    str_is_blank,
    str_is_empty,
    str_is_not,
    str_check_exact,
    str_last_char,
    str_none_to_empty,
    str_not_empty,
    str_startswith,
    str_or_empty,
    str_or_none,
    str_eq,
    str_ne,
    str_len,
)

from _bench_util import BenchSession

ASCII_SHORT = "hello"
ASCII_MID = "a" * 64 + "needle" + "b" * 64
ASCII_LONG = "x" * 4096 + "needle" + "y" * 64
NON_ASCII = "café" + "x" * 32
DIGITS = "123456"
ALPHA = "AbCdEf"
BLANK = " \t\n"
EMPTY = ""


def main() -> None:
    session = BenchSession("cystr — helpers vs plain Python (tier A)")
    session.header()

    session.section("str_contains / find / str_startswith / str_endswith  [primary: str_contains]")
    session.compare("str_contains", str_contains, lambda h, n: n in h, ASCII_SHORT, "ell", param="hit short")
    session.compare("str_contains", str_contains, lambda h, n: n in h, ASCII_SHORT, "zz", param="miss short")
    session.compare("str_contains", str_contains, lambda h, n: n in h, ASCII_MID, "needle", param="hit mid")
    session.compare("str_contains", str_contains, lambda h, n: n in h, ASCII_LONG, "needle", param="hit 4k")
    session.compare("str_contains", str_contains, lambda h, n: n in h, NON_ASCII, "fé", param="non-ascii")
    session.compare("find", find, str.find, ASCII_MID, "needle", param="hit mid")
    session.compare("find", find, str.find, ASCII_MID, "zzz", param="miss mid")
    session.compare("str_startswith", str_startswith, str.startswith, ASCII_SHORT, "he", param="hit")
    session.compare("str_startswith", str_startswith, str.startswith, ASCII_SHORT, "zz", param="miss")
    session.compare("str_endswith", str_endswith, str.endswith, ASCII_SHORT, "lo", param="hit")
    session.compare("str_endswith", str_endswith, str.endswith, ASCII_SHORT, "zz", param="miss")

    session.section("str_eq / str_len / empty / type guards")
    session.compare("str_eq", str_eq, lambda a, b: a == b, ASCII_SHORT, ASCII_SHORT, param="eq same")
    session.compare("str_eq", str_eq, lambda a, b: a == b, ASCII_SHORT, "hallo", param="ne")
    session.compare("str_eq", str_eq, lambda a, b: a == b, NON_ASCII, NON_ASCII, param="non-ascii eq")
    session.compare("str_ne", str_ne, lambda a, b: a != b, ASCII_SHORT, "hallo", param="ne")
    session.compare("str_len", str_len, len, ASCII_MID, param="n=70")
    session.compare("str_is_empty", str_is_empty, lambda s: len(s) == 0, EMPTY, param="empty")
    session.compare("str_not_empty", str_not_empty, lambda s: len(s) != 0, ASCII_SHORT, param="nonempty")
    session.compare("str_check_exact", str_check_exact, lambda o: type(o) is str, ASCII_SHORT, param="str")
    session.compare("str_is_not", str_is_not, lambda o: type(o) is not str, 1, param="int")
    session.compare("str_as_or_empty", str_as_or_empty, lambda o: o if type(o) is str else "", ASCII_SHORT, param="str")
    session.compare("str_none_to_empty", str_none_to_empty, lambda o: "" if o is None else (o if type(o) is str else ""), None, param="None")
    session.compare("str_or_none", str_or_none, lambda o: o if type(o) is str else None, 1, param="int")
    session.compare("str_or_empty", str_or_empty, lambda o: o if (type(o) is str and o) else "", "", param="empty str")

    session.section("char / str_concat / ascii classifiers")
    session.compare("str_char_at", str_char_at, lambda s, i: ord(s[i]), ASCII_SHORT, 1, param="i=1")
    session.compare("str_first_char", str_first_char, lambda s: ord(s[0]), ASCII_SHORT, param="first")
    session.compare("str_last_char", str_last_char, lambda s: ord(s[-1]), ASCII_SHORT, param="last")
    session.compare("str_concat", str_concat, lambda a, b: a + b, "ab", "cd", param="2")
    session.compare("str_concat3", str_concat3, lambda a, b, c: a + b + c, "a", "b", "c", param="3")
    session.compare("str_concat4", str_concat4, lambda a, b, c, d: a + b + c + d, "a", "b", "c", "d", param="4")
    session.compare("is_ascii", is_ascii, lambda s: s.isascii(), ASCII_MID, param="ascii mid")
    session.compare("is_ascii", is_ascii, lambda s: s.isascii(), NON_ASCII, param="non-ascii")
    session.compare("str_is_blank", str_is_blank, lambda s: not s.strip(), BLANK, param="ws")
    session.compare("str_all_digits", str_all_digits, lambda s: s.isdigit() and s.isascii(), DIGITS, param="digits")
    session.compare("str_all_alpha_ascii", str_all_alpha_ascii, lambda s: s.isalpha() and s.isascii(), ALPHA, param="alpha")
    session.compare("str_all_alnum_ascii", str_all_alnum_ascii, lambda s: s.isalnum() and s.isascii(), "A1b2", param="alnum")

    session.summary()


if __name__ == "__main__":
    main()
