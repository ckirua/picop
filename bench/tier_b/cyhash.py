"""Tier B: buffer hashing vs typed Cython baselines."""
from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session


def main() -> None:
    tb = ensure_ext("cyhash")
    view = memoryview(bytes(range(64)))
    plain = object()
    payload = bytes(range(64))

    session = tier_b_session("cyhash — Tier B")
    session.header()
    print(f"inner loop N={N:,}")
    print()

    session.section("hash_buffer vs bytes copy + hash")
    session.compare("hash_buffer(memoryview)", tb.cypy_hash_buffer, tb.baseline_hash_buffer, view, N)
    session.compare("hash_buffer(range 8:56)", tb.cypy_hash_range, tb.baseline_hash_range, view, N)
    session.compare("hash_buffer(memoryview) vs the cached builtin", tb.cypy_hash_buffer, tb.baseline_hash_cached, view, N)

    session.section("cimport-only helpers vs builtin hash()")
    session.compare("hash_generic", tb.cypy_hash_generic, tb.baseline_hash_builtin, plain, N)
    session.compare("hash_pointer", tb.cypy_hash_pointer, tb.baseline_hash_builtin, plain, N)
    session.compare("hash_buffer_raw (raw pointer)", tb.cypy_hash_raw, tb.baseline_hash_buffer, payload, N)

    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
