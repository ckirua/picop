"""Tier A inventory: remaining accessors / mutators still missing compares.

Run: CPY_BENCH_RUNS=11 python bench/cyaccessors_inventory_bench.py
"""

from __future__ import annotations

import ctypes
import json
import operator
import sys
import types
import weakref
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    capsule_is_valid,
    cell_set,
    func_get_closure,
    func_get_module,
    func_new,
    func_set_closure,
    func_set_defaults,
    long_as_longlong,
    long_as_ulong,
    long_as_ulong_mask,
    long_as_ulonglong,
    long_as_ulonglong_mask,
    long_from_longlong,
    long_from_size,
    long_from_ulong,
    long_from_ulonglong,
    map_del,
    map_del_cstr,
    map_has_key_cstr,
    map_items,
    map_setitem_cstr,
    map_values,
    mod_add_cstr,
    mod_add_int,
    mod_add_object_ref,
    mod_get_filename,
    mod_import_object,
    mod_new,
    num_divmod,
    num_float,
    num_inplace_and,
    num_inplace_floordiv,
    num_inplace_lshift,
    num_inplace_matmul,
    num_inplace_mod,
    num_inplace_mul,
    num_inplace_or,
    num_inplace_pow,
    num_inplace_rshift,
    num_inplace_sub,
    num_inplace_truediv,
    num_inplace_xor,
    num_invert,
    num_lshift,
    num_matmul,
    num_or,
    num_pos,
    num_rshift,
    num_sub,
    num_xor,
    obj_as_fd,
    obj_bytes,
    obj_call,
    obj_call_object,
    obj_delattr,
    obj_delattr_cstr,
    obj_delitem,
    obj_dir,
    obj_format,
    obj_getattr_cstr,
    obj_hasattr_cstr,
    obj_issubclass,
    obj_iter,
    obj_length_hint,
    obj_not,
    obj_repr,
    obj_richcompare,
    obj_setattr,
    obj_setattr_cstr,
    obj_setitem,
    seq_del,
    seq_del_slice,
    seq_inplace_concat,
    seq_inplace_repeat,
    seq_set,
    seq_set_slice,
    tuple_pack4,
    weakref_check_proxy,
    weakref_check_ref,
    weakref_new_proxy,
)

from _bench_util import BenchSession

EQ = 2


class _Mat:
    def __matmul__(self, other: object) -> int:
        return 7

    def __imatmul__(self, other: object) -> _Mat:
        return self


def _make_capsule() -> object:
    PyCapsule_New = ctypes.pythonapi.PyCapsule_New
    PyCapsule_New.restype = ctypes.py_object
    PyCapsule_New.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p]
    return PyCapsule_New(ctypes.c_void_p(1), b"cypy.accessors", None)


def _capsule_is_valid_py(capsule: object, name: bytes) -> bool:
    PyCapsule_IsValid = ctypes.pythonapi.PyCapsule_IsValid
    PyCapsule_IsValid.restype = ctypes.c_int
    PyCapsule_IsValid.argtypes = [ctypes.py_object, ctypes.c_char_p]
    return bool(PyCapsule_IsValid(capsule, name))


def _outer_cell() -> object:
    x = 1

    def inner() -> int:
        return x

    return inner.__closure__[0]


def main() -> None:
    session = BenchSession("cyaccessors — remaining accessors/mutators (tier A)")
    session.header()

    session.section("num")
    session.compare("num_sub", num_sub, operator.sub, 9, 4, param="9-4")
    session.compare("num_or", num_or, operator.or_, 0b1100, 0b1010, param="or")
    session.compare("num_xor", num_xor, operator.xor, 0b1100, 0b1010, param="xor")
    session.compare("num_lshift", num_lshift, operator.lshift, 3, 2, param="<<")
    session.compare("num_rshift", num_rshift, operator.rshift, 12, 2, param=">>")
    session.compare("num_divmod", num_divmod, divmod, 17, 5, param="divmod")
    session.compare("num_float", num_float, float, 7, param="float")
    session.compare("num_pos", num_pos, operator.pos, -3, param="pos")
    session.compare("num_invert", num_invert, operator.invert, 5, param="~")
    session.compare("num_matmul", num_matmul, operator.matmul, _Mat(), _Mat(), param="@")
    session.compare_mutate(
        "num_inplace_sub", num_inplace_sub, operator.isub, 10, int, 3, param="-="
    )
    session.compare_mutate(
        "num_inplace_mul", num_inplace_mul, operator.imul, 6, int, 7, param="*="
    )
    session.compare_mutate(
        "num_inplace_floordiv",
        num_inplace_floordiv,
        operator.ifloordiv,
        17,
        int,
        5,
        param="//=",
    )
    session.compare_mutate(
        "num_inplace_truediv",
        num_inplace_truediv,
        operator.itruediv,
        17.0,
        float,
        5.0,
        param="/=",
    )
    session.compare_mutate(
        "num_inplace_mod", num_inplace_mod, operator.imod, 17, int, 5, param="%="
    )
    session.compare_mutate(
        "num_inplace_pow",
        num_inplace_pow,
        lambda a, b: operator.ipow(a, b),
        2,
        int,
        8,
        param="**=",
    )
    session.compare_mutate(
        "num_inplace_lshift", num_inplace_lshift, operator.ilshift, 3, int, 2, param="<<="
    )
    session.compare_mutate(
        "num_inplace_rshift", num_inplace_rshift, operator.irshift, 12, int, 2, param=">>="
    )
    session.compare_mutate(
        "num_inplace_and", num_inplace_and, operator.iand, 0b1111, int, 0b1010, param="&="
    )
    session.compare_mutate(
        "num_inplace_or", num_inplace_or, operator.ior, 0b1100, int, 0b0011, param="|="
    )
    session.compare_mutate(
        "num_inplace_xor", num_inplace_xor, operator.ixor, 0b1100, int, 0b1010, param="^="
    )
    session.compare_mutate(
        "num_inplace_matmul",
        num_inplace_matmul,
        operator.imatmul,
        _Mat(),
        lambda _t: _Mat(),
        _Mat(),
        param="@=",
    )

    session.section("long")
    session.compare("long_from_ulong", long_from_ulong, int, 42, param="from")
    session.compare("long_from_size", long_from_size, int, 99, param="from")
    session.compare("long_from_longlong", long_from_longlong, int, 10**12, param="from")
    session.compare(
        "long_from_ulonglong", long_from_ulonglong, int, 10**12, param="from"
    )
    session.compare("long_as_ulong", long_as_ulong, int, 42, param="as")
    session.compare("long_as_longlong", long_as_longlong, int, 10**12, param="as")
    session.compare("long_as_ulonglong", long_as_ulonglong, int, 10**12, param="as")
    session.compare("long_as_ulong_mask", long_as_ulong_mask, lambda x: x & 0xFFFFFFFFFFFFFFFF, 42, param="mask")
    session.compare(
        "long_as_ulonglong_mask",
        long_as_ulonglong_mask,
        lambda x: x & 0xFFFFFFFFFFFFFFFF,
        42,
        param="mask",
    )

    session.section("map / seq")
    d = {"a": 1, "b": 2}
    session.compare("map_items", map_items, lambda o: list(o.items()), d, param="items")
    session.compare("map_values", map_values, lambda o: list(o.values()), d, param="values")
    session.compare(
        "map_has_key_cstr",
        map_has_key_cstr,
        lambda o, k: k.decode() in o,
        d,
        b"a",
        param="hit",
    )
    session.compare_mutate(
        "map_del",
        map_del,
        lambda o, k: o.__delitem__(k) or 0,
        {"a": 1, "b": 2},
        dict,
        "a",
        param="del",
    )
    session.compare_mutate(
        "map_del_cstr",
        map_del_cstr,
        lambda o, k: o.__delitem__(k.decode()) or 0,
        {"a": 1, "b": 2},
        dict,
        b"a",
        param="del",
    )
    session.compare_mutate(
        "map_setitem_cstr",
        map_setitem_cstr,
        lambda o, k, v: o.__setitem__(k.decode(), v) or 0,
        {"a": 1},
        dict,
        b"b",
        2,
        param="set",
    )
    L = [1, 2, 3, 4]
    session.compare_mutate(
        "seq_set", seq_set, lambda o, i, v: o.__setitem__(i, v) or 0, L, list, 1, 9, param="set"
    )
    session.compare_mutate(
        "seq_del", seq_del, lambda o, i: o.__delitem__(i) or 0, L, list, 1, param="del"
    )
    session.compare_mutate(
        "seq_set_slice",
        seq_set_slice,
        lambda o, a, b, v: o.__setitem__(slice(a, b), v) or 0,
        L,
        list,
        1,
        3,
        [8, 9],
        param="setslice",
    )
    session.compare_mutate(
        "seq_del_slice",
        seq_del_slice,
        lambda o, a, b: o.__delitem__(slice(a, b)) or 0,
        L,
        list,
        1,
        3,
        param="delslice",
    )
    session.compare_mutate(
        "seq_inplace_concat",
        seq_inplace_concat,
        operator.iadd,
        [1, 2],
        list,
        [3],
        param="+=",
    )
    session.compare_mutate(
        "seq_inplace_repeat",
        seq_inplace_repeat,
        operator.imul,
        [1, 2],
        list,
        3,
        param="*=",
    )

    session.section("obj")

    class Box:
        a = 1

    box = Box()
    session.compare("obj_repr", obj_repr, repr, 42, param="42")
    session.compare("obj_bytes", obj_bytes, bytes, b"abc", param="bytes")
    session.compare("obj_not", obj_not, lambda o: not o, 0, param="not")
    session.compare("obj_issubclass", obj_issubclass, issubclass, bool, int, param="bool")
    session.compare("obj_iter", obj_iter, iter, [1, 2, 3], param="iter")
    session.compare("obj_dir", obj_dir, dir, box, param="dir")
    session.compare("obj_format", obj_format, format, 42, "04d", param="fmt")
    session.compare(
        "obj_length_hint", obj_length_hint, operator.length_hint, [1, 2, 3], 0, param="hint"
    )
    session.compare(
        "obj_richcompare",
        obj_richcompare,
        lambda a, b, op: a == b,
        1,
        1,
        EQ,
        param="==",
    )
    session.compare(
        "obj_call",
        obj_call,
        lambda f, a, k=None: f(*a, **(k or {})),
        max,
        (1, 5, 3),
        None,
        param="call",
    )
    session.compare(
        "obj_call_object", obj_call_object, lambda f, a: f(*a), max, (1, 5, 3), param="call"
    )
    session.compare(
        "obj_hasattr_cstr",
        obj_hasattr_cstr,
        lambda o, n: hasattr(o, n.decode()),
        box,
        b"a",
        param="hit",
    )
    session.compare(
        "obj_getattr_cstr",
        obj_getattr_cstr,
        lambda o, n: getattr(o, n.decode()),
        box,
        b"a",
        param="get",
    )
    session.compare_mutate(
        "obj_setattr",
        obj_setattr,
        lambda o, n, v: setattr(o, n, v) or 0,
        Box(),
        lambda _t: Box(),
        "x",
        1,
        param="set",
    )
    session.compare_mutate(
        "obj_setattr_cstr",
        obj_setattr_cstr,
        lambda o, n, v: setattr(o, n.decode(), v) or 0,
        Box(),
        lambda _t: Box(),
        b"x",
        1,
        param="set",
    )
    def _box_with_x(_t: object = None) -> Box:
        o = Box()
        o.x = 1
        return o

    session.compare_mutate(
        "obj_delattr",
        obj_delattr,
        lambda o, n: delattr(o, n) or 0,
        _box_with_x(),
        _box_with_x,
        "x",
        param="del",
    )
    session.compare_mutate(
        "obj_delattr_cstr",
        obj_delattr_cstr,
        lambda o, n: delattr(o, n.decode()) or 0,
        _box_with_x(),
        _box_with_x,
        b"x",
        param="del",
    )
    session.compare_mutate(
        "obj_setitem",
        obj_setitem,
        lambda o, k, v: o.__setitem__(k, v) or 0,
        {"a": 1},
        dict,
        "b",
        2,
        param="set",
    )
    session.compare_mutate(
        "obj_delitem",
        obj_delitem,
        lambda o, k: o.__delitem__(k) or 0,
        {"a": 1, "b": 2},
        dict,
        "a",
        param="del",
    )
    f = open(__file__, "rb")
    try:
        session.compare("obj_as_fd", obj_as_fd, lambda o: o.fileno(), f, param="fd")
    finally:
        f.close()

    session.section("tuple / func / cell / capsule / weakref / mod")
    session.compare(
        "tuple_pack4", tuple_pack4, lambda a, b, c, d: (a, b, c, d), 1, 2, 3, 4, param="4"
    )

    def _f(x: int = 1) -> int:
        return x

    session.compare("func_get_module", func_get_module, lambda fn: fn.__module__, _f, param="mod")
    session.compare(
        "func_get_closure",
        func_get_closure,
        lambda fn: fn.__closure__,
        (lambda: None),
        param="none",
    )
    session.compare("func_new", func_new, types.FunctionType, _f.__code__, _f.__globals__, param="new")
    session.compare_mutate(
        "func_set_defaults",
        func_set_defaults,
        lambda fn, d: setattr(fn, "__defaults__", d) or 0,
        _f,
        lambda _t: (lambda x=1: x),
        (2,),
        param="defaults",
    )
    session.compare_mutate(
        "func_set_closure",
        func_set_closure,
        lambda fn, c: 0,  # Python has no public setter; cypy only
        (lambda: None),
        lambda _t: (lambda: None),
        None,
        param="none",
    )
    session.compare_mutate(
        "cell_set",
        cell_set,
        lambda c, v: setattr(c, "cell_contents", v) or 0,
        _outer_cell(),
        lambda _t: _outer_cell(),
        7,
        param="set",
    )
    cap = _make_capsule()
    session.compare(
        "capsule_is_valid",
        capsule_is_valid,
        _capsule_is_valid_py,
        cap,
        b"cypy.accessors",
        param="valid",
    )

    class _W:
        pass

    wobj = _W()
    session.compare(
        "weakref_check_proxy",
        weakref_check_proxy,
        lambda o: isinstance(o, weakref.ProxyTypes),
        weakref.proxy(wobj),
        param="proxy",
    )
    session.compare(
        "weakref_check_ref",
        weakref_check_ref,
        lambda o: type(o) is weakref.ref,
        weakref.ref(wobj),
        param="ref",
    )
    session.compare(
        "weakref_new_proxy", weakref_new_proxy, weakref.proxy, wobj, None, param="new"
    )
    session.compare(
        "mod_new", mod_new, lambda n: types.ModuleType(n.decode()), b"cypy_acc_mod", param="new"
    )
    session.compare("mod_get_filename", mod_get_filename, lambda m: m.__file__, json, param="json")
    session.compare("mod_import_object", mod_import_object, __import__, "math", param="math")
    session.compare_mutate(
        "mod_add_int",
        mod_add_int,
        lambda m, k, v: setattr(m, k.decode(), v) or 0,
        mod_new(b"cypy_acc_i"),
        lambda _t: mod_new(b"cypy_acc_i"),
        b"N",
        1,
        param="int",
    )
    session.compare_mutate(
        "mod_add_cstr",
        mod_add_cstr,
        lambda m, k, v: setattr(m, k.decode(), v.decode() if isinstance(v, bytes) else v) or 0,
        mod_new(b"cypy_acc_s"),
        lambda _t: mod_new(b"cypy_acc_s"),
        b"S",
        b"x",
        param="cstr",
    )
    session.compare_mutate(
        "mod_add_object_ref",
        mod_add_object_ref,
        lambda m, k, v: setattr(m, k.decode(), v) or 0,
        mod_new(b"cypy_acc_o"),
        lambda _t: mod_new(b"cypy_acc_o"),
        b"O",
        object(),
        param="obj",
    )

    session.summary()


if __name__ == "__main__":
    main()
