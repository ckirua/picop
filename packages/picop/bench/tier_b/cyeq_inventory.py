"""Tier B inventory: every public ``*_eq`` vs typed Cython ``==`` cdef loops.

Run::

    python -m bench.tier_b.build cyeq_containers cyeq_buffers cyeq_scalars cyeq_misc
    python -m bench.tier_b.cyeq_inventory

Env: ``CPY_TIERB_N`` (default 2_000_000), ``CPY_BENCH_RUNS`` (default 5).
Heavy shapes (n=64 / 1KiB) use a reduced inner-loop count.
"""

from __future__ import annotations

import datetime as dt
import sys
import weakref
from array import array
from collections import deque
from contextvars import Context, ContextVar

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session

# Heavy elementwise / memcmp cases — keep wall time practical.
N_HEAVY = max(50_000, N // 40)


def _outer(x: object) -> object:
    def _inner() -> object:
        return x

    return _inner


def _f() -> None:
    return None


def _g() -> None:
    return None


class _C:
    def m(self) -> None:
        return None


def _gen() -> object:
    yield 1


def _make_capsule() -> object:
    import ctypes

    PyCapsule_New = ctypes.pythonapi.PyCapsule_New
    PyCapsule_New.restype = ctypes.py_object
    PyCapsule_New.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p]
    return PyCapsule_New(ctypes.c_void_p(1), b"cypy.tierb.eq", None)


def main() -> None:
    containers = ensure_ext("cyeq_containers")
    buffers = ensure_ext("cyeq_buffers")
    scalars = ensure_ext("cyeq_scalars")
    misc = ensure_ext("cyeq_misc")

    session = tier_b_session(
        "cyeq_inventory — Tier B (cypy *_eq vs typed Cython == cdef loop)"
    )
    session.header()
    print(f"inner loop N={N:,}  (heavy shapes N_HEAVY={N_HEAVY:,})")
    print()

    # --- containers ---
    L = [1, 2, 3, 4, 5]
    L2 = [1, 2, 3, 4, 5]
    Lne = [1, 2, 3, 4, 6]
    L64 = list(range(64))
    L64b = list(range(64))
    T = (1, 2, 3, 4, 5)
    T2 = (1, 2, 3, 4, 5)
    Tne = (1, 2, 3, 4, 6)
    T64 = tuple(range(64))
    T64b = tuple(range(64))
    D = {"a": 1, "b": 2, "c": 3}
    D2 = {"a": 1, "b": 2, "c": 3}
    Dne = {"a": 1, "b": 2, "c": 9}
    S = {1, 2, 3, 4, 5}
    S2 = {1, 2, 3, 4, 5}
    Sne = {1, 2, 3, 4, 9}
    FS = frozenset(S)
    FS2 = frozenset(S2)
    DQ = deque([1, 2, 3, 4, 5])
    DQ2 = deque([1, 2, 3, 4, 5])
    DQne = deque([1, 2, 3, 4, 6])
    DQ64 = deque(range(64))
    DQ64b = deque(range(64))
    RG = range(0, 10, 2)
    RG2 = range(0, 10, 2)
    RGne = range(0, 10, 3)
    RGeq = range(10)  # equivalent empty-span sibling exercised separately
    RGeq2 = range(0, 10)

    session.section("containers: list / tuple / seq")
    session.compare(
        "list_eq", containers.cypy_list_eq, containers.baseline_list_eq, L, L2, N, param="eq small"
    )
    session.compare(
        "list_eq", containers.cypy_list_eq, containers.baseline_list_eq, L, Lne, N, param="ne small"
    )
    session.compare(
        "list_eq", containers.cypy_list_eq, containers.baseline_list_eq, L, L, N, param="identity"
    )
    session.compare(
        "list_eq",
        containers.cypy_list_eq,
        containers.baseline_list_eq,
        L64,
        L64b,
        N_HEAVY,
        param="eq n=64",
    )
    session.compare(
        "tuple_eq", containers.cypy_tuple_eq, containers.baseline_tuple_eq, T, T2, N, param="eq small"
    )
    session.compare(
        "tuple_eq", containers.cypy_tuple_eq, containers.baseline_tuple_eq, T, Tne, N, param="ne small"
    )
    session.compare(
        "tuple_eq", containers.cypy_tuple_eq, containers.baseline_tuple_eq, T, T, N, param="identity"
    )
    session.compare(
        "tuple_eq",
        containers.cypy_tuple_eq,
        containers.baseline_tuple_eq,
        T64,
        T64b,
        N_HEAVY,
        param="eq n=64",
    )
    session.compare(
        "seq_eq", containers.cypy_seq_eq, containers.baseline_seq_eq, L, L2, N, param="list eq"
    )
    session.compare(
        "seq_eq", containers.cypy_seq_eq, containers.baseline_seq_eq, T, L2, N, param="tuple↔list eq"
    )
    session.compare(
        "seq_eq", containers.cypy_seq_eq, containers.baseline_seq_eq, L, Lne, N, param="list ne"
    )

    session.section("containers: dict / set / frozenset / map")
    session.compare(
        "dict_eq", containers.cypy_dict_eq, containers.baseline_dict_eq, D, D2, N, param="eq small"
    )
    session.compare(
        "dict_eq", containers.cypy_dict_eq, containers.baseline_dict_eq, D, Dne, N, param="ne small"
    )
    session.compare(
        "dict_eq", containers.cypy_dict_eq, containers.baseline_dict_eq, D, D, N, param="identity"
    )
    session.compare(
        "set_eq", containers.cypy_set_eq, containers.baseline_set_eq, S, S2, N, param="eq small"
    )
    session.compare(
        "set_eq", containers.cypy_set_eq, containers.baseline_set_eq, S, Sne, N, param="ne small"
    )
    session.compare(
        "frozenset_eq",
        containers.cypy_frozenset_eq,
        containers.baseline_frozenset_eq,
        FS,
        FS2,
        N,
        param="eq",
    )
    session.compare(
        "frozenset_eq",
        containers.cypy_frozenset_eq,
        containers.baseline_frozenset_eq,
        FS,
        frozenset(Sne),
        N,
        param="ne",
    )
    session.compare(
        "map_eq", containers.cypy_map_eq, containers.baseline_map_eq, D, D2, N, param="dict eq"
    )
    session.compare(
        "map_eq", containers.cypy_map_eq, containers.baseline_map_eq, D, Dne, N, param="dict ne"
    )

    session.section("containers: deque / range")
    session.compare(
        "deque_eq", containers.cypy_deque_eq, containers.baseline_deque_eq, DQ, DQ2, N, param="eq small"
    )
    session.compare(
        "deque_eq",
        containers.cypy_deque_eq,
        containers.baseline_deque_eq,
        DQ,
        DQne,
        N,
        param="ne small",
    )
    session.compare(
        "deque_eq", containers.cypy_deque_eq, containers.baseline_deque_eq, DQ, DQ, N, param="identity"
    )
    session.compare(
        "deque_eq",
        containers.cypy_deque_eq,
        containers.baseline_deque_eq,
        DQ64,
        DQ64b,
        N_HEAVY,
        param="eq n=64",
    )
    session.compare(
        "range_eq", containers.cypy_range_eq, containers.baseline_range_eq, RG, RG2, N, param="eq"
    )
    session.compare(
        "range_eq", containers.cypy_range_eq, containers.baseline_range_eq, RG, RGne, N, param="ne"
    )
    session.compare(
        "range_eq",
        containers.cypy_range_eq,
        containers.baseline_range_eq,
        RGeq,
        RGeq2,
        N,
        param="equiv span",
    )

    # --- buffers ---
    B = b"BTCUSDT"
    B2 = b"BTCUSDT"
    Bne = b"ETHUSDT"
    B1K = b"a" * 1024
    B1Kb = b"a" * 1024
    BA = bytearray(B)
    BA2 = bytearray(B)
    BAne = bytearray(Bne)
    BA1K = bytearray(B1K)
    BA1Kb = bytearray(B1Kb)
    AY = array("i", [1, 2, 3, 4, 5])
    AY2 = array("i", [1, 2, 3, 4, 5])
    AYne = array("i", [1, 2, 3, 4, 9])
    AY64 = array("i", range(64))
    AY64b = array("i", range(64))
    MV = memoryview(b"abcdefgh")
    MV2 = memoryview(b"abcdefgh")
    MVne = memoryview(b"abcdefgX")
    ST = "hello"
    ST2 = "hello"
    STne = "hallo"
    STuni = "héllo"
    STuni2 = "héllo"

    session.section("buffers: bytes / bytes_bytearray / bytearray")
    session.compare(
        "bytes_eq", buffers.cypy_bytes_eq, buffers.baseline_bytes_eq, B, B2, N, param="eq short"
    )
    session.compare(
        "bytes_eq", buffers.cypy_bytes_eq, buffers.baseline_bytes_eq, B, Bne, N, param="ne short"
    )
    session.compare(
        "bytes_eq",
        buffers.cypy_bytes_eq,
        buffers.baseline_bytes_eq,
        B1K,
        B1Kb,
        N_HEAVY,
        param="eq 1KiB",
    )
    session.compare(
        "bytes_bytearray_eq",
        buffers.cypy_bytes_bytearray_eq,
        buffers.baseline_bytes_bytearray_eq,
        B,
        BA2,
        N,
        param="bytes→ba eq",
    )
    session.compare(
        "bytes_bytearray_eq",
        buffers.cypy_bytes_bytearray_eq,
        buffers.baseline_bytes_bytearray_eq,
        BA,
        B2,
        N,
        param="ba→bytes eq",
    )
    session.compare(
        "bytes_bytearray_eq",
        buffers.cypy_bytes_bytearray_eq,
        buffers.baseline_bytes_bytearray_eq,
        B,
        BAne,
        N,
        param="bytes→ba ne",
    )
    session.compare(
        "bytearray_eq",
        buffers.cypy_bytearray_eq,
        buffers.baseline_bytearray_eq,
        BA,
        BA2,
        N,
        param="eq short",
    )
    session.compare(
        "bytearray_eq",
        buffers.cypy_bytearray_eq,
        buffers.baseline_bytearray_eq,
        BA,
        BAne,
        N,
        param="ne short",
    )
    session.compare(
        "bytearray_eq",
        buffers.cypy_bytearray_eq,
        buffers.baseline_bytearray_eq,
        BA1K,
        BA1Kb,
        N_HEAVY,
        param="eq 1KiB",
    )

    session.section("buffers: array / memoryview / buf / str / unicode")
    session.compare(
        "array_eq", buffers.cypy_array_eq, buffers.baseline_array_eq, AY, AY2, N, param="eq small"
    )
    session.compare(
        "array_eq", buffers.cypy_array_eq, buffers.baseline_array_eq, AY, AYne, N, param="ne small"
    )
    session.compare(
        "array_eq",
        buffers.cypy_array_eq,
        buffers.baseline_array_eq,
        AY64,
        AY64b,
        N_HEAVY,
        param="eq n=64",
    )
    session.compare(
        "memoryview_eq",
        buffers.cypy_memoryview_eq,
        buffers.baseline_memoryview_eq,
        MV,
        MV2,
        N,
        param="eq",
    )
    session.compare(
        "memoryview_eq",
        buffers.cypy_memoryview_eq,
        buffers.baseline_memoryview_eq,
        MV,
        MVne,
        N,
        param="ne",
    )
    session.compare(
        "buf_eq", buffers.cypy_buf_eq, buffers.baseline_buf_eq, B, BA, N, param="bytes↔ba"
    )
    session.compare(
        "buf_eq", buffers.cypy_buf_eq, buffers.baseline_buf_eq, MV, memoryview(B[:8]), N, param="mv↔mv"
    )
    session.compare(
        "buf_eq", buffers.cypy_buf_eq, buffers.baseline_buf_eq, B, Bne, N, param="ne"
    )
    session.compare(
        "str_eq", buffers.cypy_str_eq, buffers.baseline_str_eq, ST, ST2, N, param="eq ascii"
    )
    session.compare(
        "str_eq", buffers.cypy_str_eq, buffers.baseline_str_eq, ST, STne, N, param="ne ascii"
    )
    session.compare(
        "unicode_eq",
        buffers.cypy_unicode_eq,
        buffers.baseline_unicode_eq,
        ST,
        ST2,
        N,
        param="ascii eq",
    )
    session.compare(
        "unicode_eq",
        buffers.cypy_unicode_eq,
        buffers.baseline_unicode_eq,
        STuni,
        STuni2,
        N,
        param="non-ascii eq",
    )

    # --- scalars ---
    d1 = dt.date(2026, 7, 22)
    d2 = dt.date(2026, 7, 22)
    dne = dt.date(2026, 7, 23)
    t1 = dt.time(12, 30, 0)
    t2 = dt.time(12, 30, 0)
    dt1 = dt.datetime(2026, 7, 22, 12, 30)
    dt2 = dt.datetime(2026, 7, 22, 12, 30)
    td1 = dt.timedelta(days=1, seconds=30)
    td2 = dt.timedelta(days=1, seconds=30)
    sl1 = slice(1, 10, 2)
    sl2 = slice(1, 10, 2)
    slne = slice(1, 10, 3)

    session.section("scalars: bool / float / long / int / complex / num")
    session.compare(
        "bool_eq", scalars.cypy_bool_eq, scalars.baseline_bool_eq, True, True, N, param="True"
    )
    session.compare(
        "bool_eq", scalars.cypy_bool_eq, scalars.baseline_bool_eq, True, False, N, param="ne"
    )
    session.compare(
        "float_eq", scalars.cypy_float_eq, scalars.baseline_float_eq, 1.5, 1.5, N, param="eq"
    )
    session.compare(
        "float_eq", scalars.cypy_float_eq, scalars.baseline_float_eq, 1.5, 1.6, N, param="ne"
    )
    session.compare(
        "long_eq", scalars.cypy_long_eq, scalars.baseline_long_eq, 42, 42, N, param="eq small"
    )
    session.compare(
        "long_eq", scalars.cypy_long_eq, scalars.baseline_long_eq, 42, 43, N, param="ne"
    )
    session.compare(
        "long_eq",
        scalars.cypy_long_eq,
        scalars.baseline_long_eq,
        2**100,
        2**100,
        N,
        param="eq big",
    )
    session.compare(
        "int_eq", scalars.cypy_int_eq, scalars.baseline_int_eq, 7, 7, N, param="eq"
    )
    session.compare(
        "complex_eq",
        scalars.cypy_complex_eq,
        scalars.baseline_complex_eq,
        1 + 2j,
        1 + 2j,
        N,
        param="eq",
    )
    session.compare(
        "complex_eq",
        scalars.cypy_complex_eq,
        scalars.baseline_complex_eq,
        1 + 2j,
        1 + 3j,
        N,
        param="ne",
    )
    session.compare(
        "num_eq", scalars.cypy_num_eq, scalars.baseline_num_eq, 3, 3.0, N, param="int↔float"
    )
    session.compare(
        "num_eq", scalars.cypy_num_eq, scalars.baseline_num_eq, 3, 4, N, param="ne"
    )

    session.section("scalars: slice / datetime")
    session.compare(
        "slice_eq", scalars.cypy_slice_eq, scalars.baseline_slice_eq, sl1, sl2, N, param="eq"
    )
    session.compare(
        "slice_eq", scalars.cypy_slice_eq, scalars.baseline_slice_eq, sl1, slne, N, param="ne"
    )
    session.compare(
        "dt_date_eq", scalars.cypy_dt_date_eq, scalars.baseline_dt_date_eq, d1, d2, N, param="eq"
    )
    session.compare(
        "dt_date_eq", scalars.cypy_dt_date_eq, scalars.baseline_dt_date_eq, d1, dne, N, param="ne"
    )
    session.compare(
        "dt_time_eq", scalars.cypy_dt_time_eq, scalars.baseline_dt_time_eq, t1, t2, N, param="eq"
    )
    session.compare(
        "dt_datetime_eq",
        scalars.cypy_dt_datetime_eq,
        scalars.baseline_dt_datetime_eq,
        dt1,
        dt2,
        N,
        param="eq",
    )
    session.compare(
        "dt_timedelta_eq",
        scalars.cypy_dt_timedelta_eq,
        scalars.baseline_dt_timedelta_eq,
        td1,
        td2,
        N,
        param="eq",
    )

    # --- misc ---
    c1 = _outer(1).__closure__[0]  # type: ignore[index]
    c1b = _outer(1).__closure__[0]  # type: ignore[index]
    c2 = _outer(2).__closure__[0]  # type: ignore[index]
    obj = _C()
    m1 = obj.m
    m2 = obj.m
    m_other = _C().m
    mod = sys.modules["sys"]
    g1 = _gen()
    g2 = _gen()
    it1 = iter([1, 2])
    it2 = iter([1, 2])
    tgt = _C()
    wr1 = weakref.ref(tgt)
    wr2 = weakref.ref(tgt)
    wr_other = weakref.ref(_C())
    cap = _make_capsule()
    cap2 = _make_capsule()
    cv = ContextVar("cypy_tb_eq", default=0)
    ctx1 = Context()
    ctx1.run(cv.set, 1)
    ctx2 = Context()
    ctx2.run(cv.set, 1)
    ctx_ne = Context()
    ctx_ne.run(cv.set, 2)

    session.section("misc: type / cell / obj")
    session.compare(
        "type_eq", misc.cypy_type_eq, misc.baseline_type_eq, int, int, N, param="identity"
    )
    session.compare(
        "type_eq", misc.cypy_type_eq, misc.baseline_type_eq, int, str, N, param="ne"
    )
    session.compare(
        "cell_eq", misc.cypy_cell_eq, misc.baseline_cell_eq, c1, c1, N, param="identity"
    )
    session.compare(
        "cell_eq", misc.cypy_cell_eq, misc.baseline_cell_eq, c1, c1b, N, param="same value"
    )
    session.compare(
        "cell_eq", misc.cypy_cell_eq, misc.baseline_cell_eq, c1, c2, N, param="ne"
    )
    session.compare(
        "obj_eq", misc.cypy_obj_eq, misc.baseline_obj_eq, 1, 1, N, param="int eq"
    )
    session.compare(
        "obj_eq",
        misc.cypy_obj_eq,
        misc.baseline_obj_eq,
        float("nan"),
        float("nan"),
        N,
        param="nan is nan",
    )

    session.section("misc: identity / method / weakref / capsule / context")
    session.compare(
        "func_eq", misc.cypy_func_eq, misc.baseline_func_eq, _f, _f, N, param="identity"
    )
    session.compare(
        "func_eq", misc.cypy_func_eq, misc.baseline_func_eq, _f, _g, N, param="ne"
    )
    session.compare(
        "method_eq", misc.cypy_method_eq, misc.baseline_method_eq, m1, m2, N, param="same bound"
    )
    session.compare(
        "method_eq",
        misc.cypy_method_eq,
        misc.baseline_method_eq,
        m1,
        m_other,
        N,
        param="diff self",
    )
    session.compare(
        "mod_eq", misc.cypy_mod_eq, misc.baseline_mod_eq, mod, mod, N, param="identity"
    )
    session.compare(
        "gen_eq", misc.cypy_gen_eq, misc.baseline_gen_eq, g1, g1, N, param="identity"
    )
    session.compare(
        "gen_eq", misc.cypy_gen_eq, misc.baseline_gen_eq, g1, g2, N, param="ne"
    )
    session.compare(
        "iter_eq", misc.cypy_iter_eq, misc.baseline_iter_eq, it1, it1, N, param="identity"
    )
    session.compare(
        "iter_eq", misc.cypy_iter_eq, misc.baseline_iter_eq, it1, it2, N, param="ne"
    )
    session.compare(
        "weakref_eq",
        misc.cypy_weakref_eq,
        misc.baseline_weakref_eq,
        wr1,
        wr2,
        N,
        param="same referent",
    )
    session.compare(
        "weakref_eq",
        misc.cypy_weakref_eq,
        misc.baseline_weakref_eq,
        wr1,
        wr1,
        N,
        param="identity",
    )
    session.compare(
        "weakref_eq",
        misc.cypy_weakref_eq,
        misc.baseline_weakref_eq,
        wr1,
        wr_other,
        N,
        param="ne referent",
    )
    session.compare(
        "capsule_eq",
        misc.cypy_capsule_eq,
        misc.baseline_capsule_eq,
        cap,
        cap,
        N,
        param="identity",
    )
    session.compare(
        "capsule_eq",
        misc.cypy_capsule_eq,
        misc.baseline_capsule_eq,
        cap,
        cap2,
        N,
        param="ne",
    )
    session.compare(
        "context_eq",
        misc.cypy_context_eq,
        misc.baseline_context_eq,
        ctx1,
        ctx2,
        N,
        param="eq values",
    )
    session.compare(
        "context_eq",
        misc.cypy_context_eq,
        misc.baseline_context_eq,
        ctx1,
        ctx_ne,
        N,
        param="ne values",
    )
    session.compare(
        "context_eq",
        misc.cypy_context_eq,
        misc.baseline_context_eq,
        ctx1,
        ctx1,
        N,
        param="identity",
    )

    session.summary()
    print("Markdown (paste under ### Tier B — *_eq):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
