"""Compare public :mod:`cypy` cymodule helpers vs plain Python (tier A).

Run: python bench/cymodule_bench.py
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
import types
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    mod_check,
    mod_check_exact,
    mod_get_name,
    mod_import,
    mod_magic_number,
    mod_new_object,
)

from _bench_util import BenchSession

import math as _math


def main() -> None:
    session = BenchSession("cymodule — public helpers vs plain Python (tier A)")
    session.header()

    session.section("mod_check  [primary: mod_get_name]")
    session.compare(
        "mod_check",
        mod_check,
        lambda o: isinstance(o, types.ModuleType),
        _math,
        param="math",
    )
    session.compare(
        "mod_check",
        mod_check,
        lambda o: isinstance(o, types.ModuleType),
        3,
        param="int",
    )
    session.compare(
        "mod_check_exact",
        mod_check_exact,
        lambda o: type(o) is types.ModuleType,
        _math,
        param="math",
    )
    session.compare("mod_get_name", mod_get_name, lambda m: m.__name__, _math, param="__name__")
    session.compare("mod_new_object", mod_new_object, types.ModuleType, "tmp_cypy_mod", param="new")
    session.compare("mod_import", mod_import, lambda n: importlib.import_module(n.decode()), b"math", param="math")
    session.compare(
        "mod_magic_number",
        mod_magic_number,
        lambda: int.from_bytes(importlib.util.MAGIC_NUMBER, "little"),
        param="magic",
    )

    session.summary()


if __name__ == "__main__":
    main()
