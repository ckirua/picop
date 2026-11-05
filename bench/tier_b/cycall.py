"""Tier B: picop.cycall helpers vs typed Cython ``cdef`` call loops.

Run from repo root::

    python -m bench.tier_b.build cycall
    python -m bench.tier_b.cycall
"""

from __future__ import annotations

import io

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session

ZERO = lambda: 7
ONE = lambda value: value + 1
TWO = lambda a, b: a + b
THREE = lambda a, b, c: a + b + c
KW = lambda a, offset=0: a + offset
STAR = lambda *args: sum(args)
KWNAMES = ("offset",)


def probes(tb) -> None:
    """Correctness/depth probes for the cimport-only call helpers."""
    results = []

    results.append(("call_vector zero args (NULL vector)", tb.cypy_call_vector_zero(ZERO, 1), 7))
    results.append(("call_vector 3 positional", tb.cypy_call_vector_n(THREE, 1, 2, 3, 4, 3, 1), 6))
    results.append(("call_vector 4 positional", tb.cypy_call_vector_n(STAR, 1, 2, 3, 4, 4, 1), 10))
    results.append(("call_vector pos+kw", tb.cypy_call_vector_kw(KW, 1, 2, KWNAMES, 1), 3))
    results.append(
        ("reserved-slot nargsf (NULL scratch, offset bit)", tb.cypy_call_vector_offset(TWO, 2, 3, 1), 5)
    )
    results.append(("reserved-slot on a bound method", tb.cypy_call_method_offset("read", io.BytesIO(b"abcdef"), 1), b"a"))

    results.append(("call_method_noargs", tb.cypy_call_method_noargs(io.BytesIO(b"abcdef"), "read", 1), b"abcdef"))
    results.append(("call_method_onearg", tb.cypy_call_method_onearg(io.BytesIO(b"abcdef"), "read", 1, 1), b"a"))
    results.append(
        ("call_method_vector (self in args[0])", tb.cypy_call_method_vector("read", io.BytesIO(b"abcdef"), 2, 1), b"ab")
    )

    try:
        tb.cypy_call_vector_n(lambda a, b: a / b, 1, 0, 1, 1, 2, 1)
        results.append(("call_vector exception propagation", "no exception", "division by zero"))
    except ZeroDivisionError as exc:
        results.append(("call_vector exception propagation", str(exc), "division by zero"))

    print("Depth probes (one call each, results compared to expectation)")
    print("| probe | got | expected | ok |")
    print("|---|---|---|---|")
    for label, got, expected in results:
        print(f"| {label} | {got!r} | {expected!r} | {got == expected} |")

    import subprocess
    import sys

    # CPython tests kwnames against NULL, not emptiness: Py_None is undefined.
    # Run in a subprocess so a crash cannot take the bench down.
    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            "import bench.tier_b.cycall_tb as m; print(m.cypy_call_vector_none_kw(lambda a: a, 1))",
        ],
        capture_output=True,
        text=True,
    )
    print(
        "Depth probe: Py_None as kwnames -> "
        f"exit={proc.returncode} stdout={proc.stdout.strip()!r} stderr={proc.stderr.strip()[:80]!r}"
    )
    print()


def main() -> None:
    ensure_ext("cycall")
    import cycall_tb as tb

    probes(tb)

    def vector_n(nargs: int):
        """Same callable and argument vector, different positional count."""

        def loop(func, a, b, c, d, n):
            return tb.cypy_call_vector_n(func, a, b, c, d, nargs, n)

        return loop

    def method_vector(obj, name, value, n):
        # ``call_method_vector`` takes the method name first (CPython convention).
        return tb.cypy_call_method_vector(name, obj, value, n)

    stream = io.BytesIO(b"abcdef")
    kwnames = KWNAMES

    session = tier_b_session("cycall — Tier B (picop helpers vs typed Cython cdef loops)")
    session.header()
    print(f"inner loop N={N:,}  ·  ratio = picop_loop / cython_baseline_loop")
    print()

    session.section("zero / one / two positional arguments")
    session.compare("call_noargs", tb.cypy_call_noargs, tb.baseline_call0, ZERO, N, param="no args")
    session.compare("call_onearg", tb.cypy_call_onearg, tb.baseline_call1, ONE, 7, N, param="one arg")
    session.compare("call_twoargs", tb.cypy_call_twoargs, tb.baseline_call2, TWO, 2, 3, N, param="two args")
    session.compare("call_vector (0 args)", tb.cypy_call_vector_zero, tb.baseline_call0, ZERO, N, param="NULL vector")

    session.section("arity 3+ and keywords (cimport-only depth path)")
    session.compare("call_vector (3 args)", tb.cypy_call_vector3, tb.baseline_call3, THREE, 1, 2, 3, N, param="three args")
    session.compare(
        "call_vector (pos+kw)", tb.cypy_call_vector_kw, tb.baseline_call_kw, KW, 1, 2, kwnames, N, param="1 pos + 1 kw"
    )
    session.compare("call_vector nargs 3 vs 2", vector_n(3), vector_n(2), STAR, 1, 2, 3, 4, N, param="arity scaling")
    session.compare("call_vector nargs 4 vs 3", vector_n(4), vector_n(3), STAR, 1, 2, 3, 4, N, param="arity scaling")
    session.compare(
        "nargsf macro vs literal", tb.cypy_nargs_macro, tb.baseline_nargs_literal, TWO, 2, 3, 2, N, param="PyVectorcall_NARGS"
    )
    session.compare(
        "reserved-slot nargsf vs plain", tb.cypy_call_vector_offset, tb.cypy_call_vector_plain2, TWO, 2, 3, N, param="offset bit"
    )

    session.section("method calls")
    session.compare(
        "call_method_noargs", tb.cypy_call_method_noargs, tb.baseline_method0, stream, "read", N, param="read()"
    )
    session.compare(
        "call_method_onearg", tb.cypy_call_method_onearg, tb.baseline_method1, stream, "read", 1, N, param="read(1)"
    )
    session.compare(
        "call_method_vector", method_vector, tb.baseline_method1, stream, "read", 1, N, param="read(1)"
    )

    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
