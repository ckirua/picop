"""Compare public :mod:`picop` hash helpers with plain Python calls (tier A)."""

from __future__ import annotations

import array
import sys
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from picop import hash_buffer  # noqa: E402
from _bench_util import BenchSession  # noqa: E402


def py_hash_copy(data):
    """The only pure-Python route for an unhashable exporter: copy, then hash."""
    return hash(bytes(data))


def py_hash_slice(data, start, end):
    return hash(data[start:end])


def main() -> None:
    mv256 = memoryview(bytes(range(256)))
    ba64 = bytearray(range(64))
    ba2048 = bytearray(bytes(range(256)) * 8)
    b8 = b"abcdefgh"
    b2048 = bytes(range(256)) * 8
    buf = array.array("B", b"abcdef")

    # Correctness of the buffer path before timing.
    assert hash_buffer(mv256) == hash(bytes(mv256)) == hash(mv256)
    assert hash_buffer(ba64, 8, 56) == hash(bytes(ba64[8:56]))
    assert hash_buffer(b8) == hash(b8)
    assert hash_buffer(buf) == hash(bytes(buf))
    assert hash_buffer(b2048, 64, 128) == hash(b2048[64:128])
    assert hash_buffer(mv256, 0, 0) == hash(b"")
    try:
        hash_buffer(memoryview(bytes(range(100)))[::2])
    except BufferError:
        pass  # CPython refuses to expose a non-contiguous buffer
    else:
        raise AssertionError("non-contiguous buffer should not be hashed")

    session = BenchSession("cyhash — public helper vs plain Python (tier A)")
    session.header()

    session.section("buffers Python cannot hash (bytearray / array.array)")
    session.compare("hash_buffer", hash_buffer, py_hash_copy, ba64, param="bytearray n=64")
    session.compare("hash_buffer", hash_buffer, py_hash_copy, ba2048, param="bytearray n=2048")
    session.compare("hash_buffer", hash_buffer, py_hash_copy, buf, param="array.array('B') n=6")

    session.section("ranges, against the builtin's slice-and-hash")
    session.compare(
        "hash_buffer", hash_buffer, py_hash_slice, b2048, 64, 128, param="bytes n=2048 range 64:128"
    )
    session.compare(
        "hash_buffer", hash_buffer, py_hash_slice, mv256, 64, 128, param="memoryview n=256 range 64:128"
    )

    session.section("objects CPython already hashes (the cache crossover)")
    session.compare("hash_buffer", hash_buffer, hash, b8, param="bytes n=8 (cached)")
    session.compare("hash_buffer", hash_buffer, hash, mv256, param="memoryview n=256 (cached)")

    session.summary()


if __name__ == "__main__":
    main()
