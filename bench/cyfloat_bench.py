"""Compare public :mod:`picop` cyfloat helpers vs plain Python (tier A).

Run: python bench/cyfloat_bench.py
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from picop import (
    float_as_double, float_check, float_check_exact, float_from_double, float_from_cstr,
)
from picop.cyfloat import float_pack8, float_pack4, float_pack2, float_unpack8, float_unpack4, float_unpack2
from _bench_util import BenchSession

F = 3.14159


def main() -> None:
    session = BenchSession("cyfloat — public helpers vs plain Python (tier A)")
    session.header()

    session.section("float_check  [primary: float_as_double]")
    session.compare("float_check", float_check, lambda o: isinstance(o, float), F, param="float")
    session.compare("float_check", float_check, lambda o: isinstance(o, float), 1, param="int")
    session.compare(
        "float_check_exact",
        float_check_exact,
        lambda o: type(o) is float,
        F,
        param="float",
    )

    session.section("from / as")
    session.compare("float_from_double", float_from_double, float, 2.5, param="2.5")
    session.compare("float_from_cstr", float_from_cstr, float, "2.5", param="'2.5'")
    session.compare("float_as_double", float_as_double, float, F, param="pi")
    session.compare("float_as_double", float_as_double, float, 7, param="int 7")

    session.section("pack / unpack vs struct")
    le8, be8 = struct.pack("<d", F), struct.pack(">d", F)
    le4, be4 = struct.pack("<f", F), struct.pack(">f", F)
    le2, be2 = struct.pack("<e", F), struct.pack(">e", F)
    session.compare("float_pack8", float_pack8, lambda x: struct.pack("<d", x), F, param="little")
    session.compare("float_unpack8", float_unpack8, lambda b: struct.unpack("<d", b)[0], le8, param="little")
    session.compare("float_pack8", lambda x: float_pack8(x, False), lambda x: struct.pack(">d", x), F, param="big")
    session.compare("float_unpack8", lambda b: float_unpack8(b, False), lambda b: struct.unpack(">d", b)[0], be8, param="big")
    session.compare("float_pack4", float_pack4, lambda x: struct.pack("<f", x), F, param="little")
    session.compare("float_unpack4", float_unpack4, lambda b: struct.unpack("<f", b)[0], le4, param="little")
    session.compare("float_pack4", lambda x: float_pack4(x, False), lambda x: struct.pack(">f", x), F, param="big")
    session.compare("float_unpack4", lambda b: float_unpack4(b, False), lambda b: struct.unpack(">f", b)[0], be4, param="big")
    session.compare("float_pack2", float_pack2, lambda x: struct.pack("<e", x), F, param="little")
    session.compare("float_unpack2", float_unpack2, lambda b: struct.unpack("<e", b)[0], le2, param="little")
    session.compare("float_pack2", lambda x: float_pack2(x, False), lambda x: struct.pack(">e", x), F, param="big")
    session.compare("float_unpack2", lambda b: float_unpack2(b, False), lambda b: struct.unpack(">e", b)[0], be2, param="big")
    session.summary()


if __name__ == "__main__":
    main()
