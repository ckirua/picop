"""Compare public :mod:`picop` code helpers with plain Python calls (tier A)."""

from __future__ import annotations

import sys
import types
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from picop import (  # noqa: E402
    code_addr2line, code_argcount, code_cellvars, code_check, code_code,
    code_consts, code_filename, code_firstlineno, code_freevars,
    code_kwonlyargcount, code_name, code_names, code_posonlyargcount,
    code_qualname, code_varnames,
)
from _bench_util import BenchSession  # noqa: E402


def make_code():
    def inner(a, b=1):
        return a + b

    return inner.__code__


def py_code_check(code):
    return isinstance(code, types.CodeType)


def py_addr2line_zero(code, addr):
    return code.co_firstlineno


def main() -> None:
    code = make_code()
    session = BenchSession("cycode — public helpers vs plain Python (tier A)")
    session.header()
    session.section("code accessors")
    session.compare("code_check", code_check, py_code_check, code, param="code_check")
    session.compare("code_name", code_name, lambda c: c.co_name, code, param="code_name")
    session.compare("code_qualname", code_qualname, lambda c: c.co_qualname, code, param="code_qualname")
    session.compare("code_filename", code_filename, lambda c: c.co_filename, code, param="code_filename")
    session.compare("code_firstlineno", code_firstlineno, lambda c: c.co_firstlineno, code, param="code_firstlineno")
    session.compare("code_argcount", code_argcount, lambda c: c.co_argcount, code, param="code_argcount")
    session.compare("code_posonlyargcount", code_posonlyargcount, lambda c: c.co_posonlyargcount, code, param="code_posonlyargcount")
    session.compare("code_kwonlyargcount", code_kwonlyargcount, lambda c: c.co_kwonlyargcount, code, param="code_kwonlyargcount")
    session.compare("code_consts", code_consts, lambda c: c.co_consts, code, param="code_consts")
    session.compare("code_names", code_names, lambda c: c.co_names, code, param="code_names")
    session.compare("code_code", code_code, lambda c: c.co_code, code, param="code_code")
    session.compare("code_varnames", code_varnames, lambda c: c.co_varnames, code, param="code_varnames")
    session.compare("code_cellvars", code_cellvars, lambda c: c.co_cellvars, code, param="code_cellvars")
    session.compare("code_freevars", code_freevars, lambda c: c.co_freevars, code, param="code_freevars")
    # The plain-Python baseline only matches the addr=0 case.
    session.compare("code_addr2line", code_addr2line, py_addr2line_zero, code, 0, param="code_addr2line (addr=0; co_firstlineno baseline)")
    session.summary()


if __name__ == "__main__":
    main()
