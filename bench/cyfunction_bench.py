"""Compare public :mod:`picop` cyfunction helpers vs plain Python (tier A).

Run: python bench/cyfunction_bench.py
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from picop import (
    func_check,
    func_get_annotations,
    func_get_code,
    func_get_defaults,
    func_get_globals,
    func_get_kw_defaults,
    func_new_with_qualname,
    func_set_annotations,
    func_set_kw_defaults,
)

from _bench_util import BenchSession


def _sample(x=1):
    return x


def _kw(a, b=1, *, c=2):
    return a


def main() -> None:
    session = BenchSession("cyfunction — public helpers vs plain Python (tier A)")
    session.header()

    session.section("func_check  [primary: func_get_code]")
    session.compare(
        "func_check",
        func_check,
        lambda o: isinstance(o, types.FunctionType),
        _sample,
        param="func",
    )
    session.compare(
        "func_check",
        func_check,
        lambda o: isinstance(o, types.FunctionType),
        len,
        param="builtin",
    )
    session.compare("func_get_code", func_get_code, lambda f: f.__code__, _sample, param="__code__")
    session.compare(
        "func_get_globals",
        func_get_globals,
        lambda f: f.__globals__,
        _sample,
        param="__globals__",
    )
    session.compare(
        "func_get_defaults",
        func_get_defaults,
        lambda f: f.__defaults__,
        _sample,
        param="__defaults__",
    )
    session.compare(
        "func_get_kw_defaults",
        func_get_kw_defaults,
        lambda f: f.__kwdefaults__,
        _kw,
        param="__kwdefaults__",
    )
    session.compare(
        "func_set_kw_defaults",
        func_set_kw_defaults,
        lambda f, d: setattr(f, "__kwdefaults__", d),
        _kw,
        {"c": 3},
        param="kw-defaults dict",
    )
    session.compare(
        "func_get_annotations",
        func_get_annotations,
        lambda f: getattr(f, "__annotations__", None),
        _sample,
        param="unset annotations",
    )
    session.compare(
        "func_set_annotations",
        func_set_annotations,
        lambda f, a: setattr(f, "__annotations__", a),
        _sample,
        {"x": int},
        param="annotations dict",
    )
    session.compare(
        "func_new_with_qualname",
        func_new_with_qualname,
        lambda code, glob, qual: (
            lambda f: (setattr(f, "__qualname__", qual), f)[0]
        )(types.FunctionType(code, glob)),
        _sample.__code__,
        _sample.__globals__,
        "Outer.sample",
        param="code + globals + qualname",
    )

    session.summary()


if __name__ == "__main__":
    main()
