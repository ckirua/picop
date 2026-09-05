"""Compare public :mod:`cypy` cytuple helpers vs plain Python (tier A).

Run from repo root::

    python bench/cytuple_bench.py

Or via ``./bench/small.sh``. Paste tables into ``docs/modules/001_cytuple.md``.

``tnew`` / ``tset`` / ``tresize`` are ``cdef`` (cimport-only) — not in this harness.
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    tuple_check,
    tuple_check_exact,
    tuple_get,
    tuple_get_checked,
    tuple_len,
    tuple_pack2,
    tuple_pack3,
    tuple_size,
    tuple_slice,
)

from _bench_util import BenchSession

PAYLOAD: tuple[str, str, str, str] = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT")


def py_tget(t: tuple[str, ...], i: int) -> str:
    return t[i]


def py_tlen(t: tuple[str, ...]) -> int:
    return len(t)


def py_tcheck(p: object) -> bool:
    return isinstance(p, tuple)


def py_tcheck_exact(p: object) -> bool:
    return type(p) is tuple


def py_tpack2(a: object, b: object) -> tuple[object, object]:
    return (a, b)


def py_tpack3(a: object, b: object, c: object) -> tuple[object, object, object]:
    return (a, b, c)


def py_tslice(t: tuple[object, ...], low: int, high: int) -> tuple[object, ...]:
    return t[low:high]


def main() -> None:
    session = BenchSession("cytuple — public helpers vs plain Python (tier A)")
    session.header()

    session.section("tuple_get vs t[i]  [primary: index=0]")
    for i in (0, 2, 3):
        session.compare("tuple_get", tuple_get, py_tget, PAYLOAD, i, param=f"index={i}")

    session.section("tuple_get_checked vs t[i]")
    for i in (0, 2, 3):
        session.compare(
            "tuple_get_checked",
            tuple_get_checked,
            py_tget,
            PAYLOAD,
            i,
            param=f"index={i}",
        )

    session.section("tuple_len vs tuple_size vs len(t)")
    session.compare("tuple_len", tuple_len, py_tlen, PAYLOAD, param="tuple_len vs len")
    session.compare("tuple_size", tuple_size, py_tlen, PAYLOAD, param="tuple_size vs len")

    session.section("tuple_check / tuple_check_exact")
    session.compare("tuple_check", tuple_check, py_tcheck, PAYLOAD, param="tuple")
    session.compare("tuple_check", tuple_check, py_tcheck, "not-a-tuple", param="str")
    session.compare(
        "tuple_check_exact",
        tuple_check_exact,
        py_tcheck_exact,
        PAYLOAD,
        param="tuple",
    )

    session.section("tuple_pack2 / tuple_pack3 vs literal")
    session.compare("tuple_pack2", tuple_pack2, py_tpack2, "a", "b", param="2")
    session.compare("tuple_pack3", tuple_pack3, py_tpack3, "a", "b", "c", param="3")

    session.section("tuple_slice vs t[low:high]")
    session.compare("tuple_slice", tuple_slice, py_tslice, PAYLOAD, 1, 3, param="1:3")

    session.summary()


if __name__ == "__main__":
    main()
