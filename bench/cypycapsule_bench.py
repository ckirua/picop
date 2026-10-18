"""Tier A benches for cypycapsule."""
from __future__ import annotations
import sys, ctypes
from pathlib import Path
_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path: sys.path.insert(0, str(_BENCH_ROOT))
from cypy import capsule_check_exact
from _bench_util import BenchSession

def main():
    session = BenchSession("cypycapsule — tier A")
    session.header()
    # create via ctypes pythonapi PyCapsule_New
    PyCapsule_New = ctypes.pythonapi.PyCapsule_New
    PyCapsule_New.restype = ctypes.py_object
    PyCapsule_New.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p]
    cap = PyCapsule_New(ctypes.c_void_p(1), b"cypy.test", None)
    session.section("capsule")
    session.compare("capsule_check_exact", capsule_check_exact, lambda o: type(o).__name__=='PyCapsule', cap, param="cap")
    session.compare("capsule_check_exact", capsule_check_exact, lambda o: type(o).__name__=='PyCapsule', 1, param="int")
    session.summary()
if __name__ == '__main__':
    main()
