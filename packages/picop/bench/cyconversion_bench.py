"""Tier A benches for cyconversion."""
from __future__ import annotations
import sys
from pathlib import Path
_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path: sys.path.insert(0, str(_BENCH_ROOT))
from cypy import conv_cstr_to_double, conv_stricmp
from _bench_util import BenchSession

def main():
    session = BenchSession("cyconversion — tier A")
    session.header()
    session.section("conv")
    session.compare("conv_cstr_to_double", conv_cstr_to_double, float, b"3.14159", param="pi")
    session.compare("conv_stricmp", conv_stricmp, lambda a,b: 0 if a.lower()==b.lower() else 1, b"AbC", b"aBc", param="icmp")
    session.summary()
if __name__ == '__main__':
    main()
