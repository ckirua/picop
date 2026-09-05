"""Tier A benches for cycodecs."""
from __future__ import annotations
import sys, codecs
from pathlib import Path
_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path: sys.path.insert(0, str(_BENCH_ROOT))
from cypy import codec_decode, codec_encode, codec_known
from _bench_util import BenchSession

def main():
    session = BenchSession("cycodecs — tier A")
    session.header()
    session.section("codec")
    session.compare("codec_known", codec_known, lambda e: bool(__import__('encodings').search_function(e.decode())), b"utf-8", param="utf-8")
    session.compare(
        "codec_encode",
        codec_encode,
        lambda s, e, err: s.encode(e.decode(), (err or b"strict").decode()),
        "café",
        b"utf-8",
        b"strict",
        param="utf-8",
    )
    session.compare(
        "codec_decode",
        codec_decode,
        lambda b, e, err: b.decode(e.decode(), (err or b"strict").decode()),
        "café".encode(),
        b"utf-8",
        b"strict",
        param="utf-8",
    )
    session.summary()
if __name__ == '__main__':
    main()
