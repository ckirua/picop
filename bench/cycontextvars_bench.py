"""Tier A benches for cycontextvars (checks + context_eq depth)."""

from __future__ import annotations

import contextvars
import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    context_eq,
    ctx_check_exact,
    ctx_copy_current,
    ctxvar_check_exact,
    ctxvar_new,
)

from _bench_util import BenchSession

VAR = contextvars.ContextVar("bench_ctx_eq", default=0)


def _empty_pair() -> tuple[contextvars.Context, contextvars.Context]:
    return contextvars.Context(), contextvars.Context()


def _filled(value: int) -> contextvars.Context:
    ctx = contextvars.Context()

    def _set() -> None:
        VAR.set(value)

    ctx.run(_set)
    return ctx


def py_eq(a: object, b: object) -> bool:
    return a == b


def main() -> None:
    session = BenchSession("cycontextvars — tier A")
    session.header()
    v = contextvars.ContextVar("t")
    session.section("ctx checks / constructors")
    session.compare(
        "ctx_check_exact",
        ctx_check_exact,
        lambda o: type(o) is contextvars.Context,
        contextvars.copy_context(),
        param="ctx",
    )
    session.compare(
        "ctxvar_check_exact",
        ctxvar_check_exact,
        lambda o: type(o) is contextvars.ContextVar,
        v,
        param="var",
    )
    session.compare(
        "ctx_copy_current",
        ctx_copy_current,
        contextvars.copy_context,
        param="copy",
    )
    session.compare(
        "ctxvar_new",
        ctxvar_new,
        lambda n, d: contextvars.ContextVar(n.decode(), default=d),
        b"x",
        None,
        param="new",
    )

    empty_a, empty_b = _empty_pair()
    filled_1 = _filled(1)
    filled_1b = _filled(1)
    filled_2 = _filled(2)
    session.section("context_eq vs `==`  [primary: empty equal]")
    session.compare("context_eq", context_eq, py_eq, empty_a, empty_b, param="eq empty")
    session.compare("context_eq", context_eq, py_eq, empty_a, empty_a, param="identity")
    session.compare("context_eq", context_eq, py_eq, filled_1, filled_1b, param="eq filled")
    session.compare("context_eq", context_eq, py_eq, filled_1, filled_2, param="ne filled")
    session.compare(
        "context_eq",
        context_eq,
        py_eq,
        filled_1,
        empty_a,
        param="ne filled/empty",
    )

    session.summary()


if __name__ == "__main__":
    main()
