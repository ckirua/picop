"""Tier B: cypycapsule vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
from ctypes import c_char_p, c_void_p, py_object, pythonapi

_PyCapsule_New = pythonapi.PyCapsule_New
_PyCapsule_New.restype = py_object
_PyCapsule_New.argtypes = [c_void_p, c_char_p, c_void_p]
PAYLOAD = _PyCapsule_New(c_void_p(1), b"tierb", None)

def main() -> None:
    tb = ensure_ext("cypycapsule")
    session = tier_b_session("cypycapsule — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("capsule_check_exact  [primary]")
    session.compare("capsule_check_exact", tb.cypy_capsule_check_exact, tb.baseline_capsule_check_exact, PAYLOAD, N, param="capsule")
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
