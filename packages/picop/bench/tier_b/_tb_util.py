"""Shared helpers for Tier B Python runners."""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_BENCH = _HERE.parent
_ROOT = _BENCH.parent
if str(_BENCH) not in sys.path:
    sys.path.insert(0, str(_BENCH))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from _bench_util import (  # noqa: E402
    N as _TIER_A_N,
    RUNS,
    WARMUP,
    BenchSession,
    CompareRow,
    _fmt_mean_std,
    _fmt_p99,
    _fmt_ratio,
)
import os

# Tier B needs a hotter inner loop than Tier A (ops are ~1 cycle with immortal refs).
N: int = int(os.environ.get("CPY_TIERB_N", os.environ.get("CPY_BENCH_N", "2_000_000")))
if N == _TIER_A_N and "CPY_TIERB_N" not in os.environ and "CPY_BENCH_N" not in os.environ:
    N = 2_000_000

__all__: list[str] = [
    "N",
    "RUNS",
    "WARMUP",
    "BenchSession",
    "ensure_ext",
    "markdown_table",
    "tier_b_session",
]


def ensure_ext(stem: str) -> object:
    """Import ``{stem}_tb``, rebuilding in-place if needed."""
    try:
        return __import__(f"{stem}_tb")
    except ImportError:
        from bench.tier_b.build import build

        build([stem])
        # Fresh import after build
        for key in list(sys.modules):
            if key == f"{stem}_tb" or key.str_startswith(f"{stem}_tb."):
                del sys.modules[key]
        return __import__(f"{stem}_tb")


def tier_b_session(title: str) -> BenchSession:
    """Session that times one Cython full-loop call per sample (N lives inside .pyx)."""
    return BenchSession(title, n=1, runs=RUNS, warmup=WARMUP)


def markdown_table(rows: list[CompareRow]) -> str:
    """Markdown table for pasting under ``### Tier B (Cython baseline)``."""
    lines = [
        "| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |",
        "|-----------|------|-------------|-----|----------------|-------|------|------|",
    ]
    for row in rows:
        note = "cypy faster" if row.ratio_mean < 0.98 else (
            "baseline faster" if row.ratio_mean > 1.02 else "~tie"
        )
        lines.append(
            "| {op} | {case} | {cy} | {p99} | {base} | **{ratio}** | {p99x} | {note} |".format(
                op=row.label,
                case=row.param or "—",
                cy=_fmt_mean_std(row.cypy),
                p99=_fmt_p99(row.cypy),
                base=_fmt_mean_std(row.baseline),
                ratio=_fmt_ratio(row.ratio_mean),
                p99x=_fmt_ratio(row.ratio_p99),
                note=note,
            )
        )
    return "\n".join(lines)
