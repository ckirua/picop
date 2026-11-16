"""Compare public :mod:`picop` cytype helpers vs plain Python (tier A).

Run: python bench/cytype_bench.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from picop.cytype import type_check, type_check_exact, type_is_subtype
from picop.cytype import type_get_name, type_get_qualname, type_get_dict

from _bench_util import BenchSession


class Sub(int):
    pass


def main() -> None:
    session = BenchSession("cytype — public helpers vs plain Python (tier A)")
    session.header()

    session.section("type_check  [primary]")
    session.compare("type_check", type_check, lambda o: isinstance(o, type), int, param="int")
    session.compare("type_check", type_check, lambda o: isinstance(o, type), 3, param="3")
    session.compare("type_check", type_check, lambda o: isinstance(o, type), Sub, param="Sub")
    session.compare(
        "type_check_exact",
        type_check_exact,
        lambda o: type(o) is type,
        int,
        param="int",
    )
    session.compare(
        "type_check_exact",
        type_check_exact,
        lambda o: type(o) is type,
        type,
        param="type",
    )
    session.compare("type_is_subtype", type_is_subtype, issubclass, bool, int, param="bool<int")
    session.compare("type_is_subtype", type_is_subtype, issubclass, int, bool, param="int!<bool")
    session.section("type metadata accessors")
    session.compare("type_get_name", type_get_name, lambda t: t.__name__, int, param="int")
    session.compare("type_get_qualname", type_get_qualname, lambda t: t.__qualname__, int, param="int")
    session.compare("type_get_dict", type_get_dict, lambda t: t.__dict__, int, param="int")
    session.compare("type_get_name", type_get_name, lambda t: t.__name__, Sub, param="Sub")

    session.summary()


if __name__ == "__main__":
    main()
