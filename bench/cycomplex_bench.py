"""Compare public :mod:`cypy` cycomplex helpers vs plain Python (tier A).

Run: python bench/cycomplex_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    complex_check,
    complex_check_exact,
    complex_from_doubles,
    complex_imag_as_double,
    complex_real_as_double,
)

from _bench_util import BenchSession

Z = 1.5 + 2.5j


class _ComplexSub(complex):
    pass


SUB = _ComplexSub(1.0, 2.0)


def main() -> None:
    session = BenchSession("cycomplex — public helpers vs plain Python (tier A)")
    session.header()

    session.section("complex_check  [primary: complex_real_as_double]")
    session.compare("complex_check", complex_check, lambda o: isinstance(o, complex), Z, param="complex")
    session.compare("complex_check", complex_check, lambda o: isinstance(o, complex), 1, param="int")
    session.compare("complex_check", complex_check, lambda o: isinstance(o, complex), SUB, param="subtype")
    session.compare(
        "complex_check_exact",
        complex_check_exact,
        lambda o: type(o) is complex,
        Z,
        param="complex",
    )
    session.compare(
        "complex_check_exact",
        complex_check_exact,
        lambda o: type(o) is complex,
        SUB,
        param="subtype",
    )

    session.section("from / real / imag")
    session.compare(
        "complex_from_doubles",
        complex_from_doubles,
        complex,
        1.5,
        2.5,
        param="1.5+2.5j",
    )
    session.compare("complex_real_as_double", complex_real_as_double, lambda z: z.real, Z, param="Z.real")
    session.compare("complex_imag_as_double", complex_imag_as_double, lambda z: z.imag, Z, param="Z.imag")
    session.compare(
        "complex_real_as_double",
        complex_real_as_double,
        float,
        7,
        param="int 7",
    )

    session.summary()


if __name__ == "__main__":
    main()
