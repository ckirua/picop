"""Tier B microbenches: typed Cython ``cdef``-loop baseline vs cypy helpers.

Build extensions first::

    python -m bench.tier_b.build

Run one module::

    python -m bench.tier_b.cytuple
    # or
    ./bench/tier_b/run.sh cytuple

See ``bench/BENCH.md`` (Tier B) and ``docs/PIPELINE.md``.
"""

from __future__ import annotations

__all__: list[str] = []
