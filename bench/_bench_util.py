"""Shared timing helpers for cypy benchmark scripts."""

from __future__ import annotations

import os
import statistics
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Literal, TypeVar

T = TypeVar("T")

# Fast defaults — override for a heavier pass: CPY_BENCH_N=500000 CPY_BENCH_RUNS=11
N: int = int(os.environ.get("CPY_BENCH_N", "80_000"))
RUNS: int = int(os.environ.get("CPY_BENCH_RUNS", "5"))
WARMUP: int = int(os.environ.get("CPY_BENCH_WARMUP", "0"))

Align = Literal["left", "right"]


@dataclass(frozen=True, slots=True)
class SampleStats:
    mean: float
    stdev: float
    variance: float
    minimum: float
    maximum: float
    median: float
    p50: float
    p95: float
    p99: float
    samples: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class CompareRow:
    label: str
    param: str
    cypy: SampleStats
    baseline: SampleStats

    @property
    def ratio_mean(self) -> float:
        if self.baseline.mean <= 0.0:
            return 0.0
        return self.cypy.mean / self.baseline.mean

    @property
    def ratio_p99(self) -> float:
        if self.baseline.p99 <= 0.0:
            return 0.0
        return self.cypy.p99 / self.baseline.p99


@dataclass
class _Section:
    title: str
    rows: list[CompareRow] = field(default_factory=list)


class TextTable:
    def __init__(self, headers: tuple[str, ...], *, aligns: tuple[Align, ...] | None = None) -> None:
        self.headers = headers
        self.aligns = aligns or ("left",) * len(headers)
        self._rows: list[tuple[str, ...]] = []

    def add(self, *cells: str) -> None:
        if len(cells) != len(self.headers):
            msg = f"expected {len(self.headers)} cells, got {len(cells)}"
            raise ValueError(msg)
        self._rows.append(cells)

    def render(self) -> list[str]:
        widths = [len(header) for header in self.headers]
        for row in self._rows:
            for index, cell in enumerate(row):
                widths[index] = max(widths[index], len(cell))

        def fmt_cell(cell: str, width: int, align: Align) -> str:
            if align == "right":
                return cell.rjust(width)
            return cell.ljust(width)

        def rule(left: str, mid: str, right: str, fill: str) -> str:
            parts = [fill * (width + 2) for width in widths]
            return left + mid.join(parts) + right

        top = rule("┌", "┬", "┐", "─")
        mid = rule("├", "┼", "┤", "─")
        bot = rule("└", "┴", "┘", "─")

        header_line = "│ " + " │ ".join(
            fmt_cell(header, widths[index], self.aligns[index])
            for index, header in enumerate(self.headers)
        ) + " │"

        body = [
            "│ "
            + " │ ".join(
                fmt_cell(cell, widths[index], self.aligns[index])
                for index, cell in enumerate(row)
            )
            + " │"
            for row in self._rows
        ]

        return [top, header_line, mid, *body, bot]


def _timed_loop(func: Callable[..., object], args: tuple[object, ...], n: int) -> float:
    t0 = time.perf_counter()
    for _ in range(n):
        func(*args)
    return time.perf_counter() - t0


def _timed_mutate_loop(
    func: Callable[..., object],
    template: object,
    factory: Callable[[T], T],
    args: tuple[object, ...],
    n: int,
) -> float:
    t0 = time.perf_counter()
    for _ in range(n):
        func(factory(template), *args)
    return time.perf_counter() - t0


def collect_stats(
    func: Callable[..., object],
    *args: object,
    n: int = N,
    runs: int = RUNS,
    warmup: int = WARMUP,
) -> SampleStats:
    for _ in range(warmup):
        _timed_loop(func, args, n)
    samples = tuple(_timed_loop(func, args, n) for _ in range(runs))
    return _make_stats(samples)


def collect_mutate_stats(
    func: Callable[..., object],
    template: T,
    factory: Callable[[T], T],
    *args: object,
    n: int = N,
    runs: int = RUNS,
    warmup: int = WARMUP,
) -> SampleStats:
    for _ in range(warmup):
        _timed_mutate_loop(func, template, factory, args, n)
    samples = tuple(
        _timed_mutate_loop(func, template, factory, args, n) for _ in range(runs)
    )
    return _make_stats(samples)


def _percentile(sorted_samples: Sequence[float], pct: float) -> float:
    """Linear-interpolation percentile on a pre-sorted sample list (pct in 0..100)."""
    if not sorted_samples:
        return 0.0
    if len(sorted_samples) == 1:
        return sorted_samples[0]
    rank = (pct / 100.0) * (len(sorted_samples) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(sorted_samples) - 1)
    frac = rank - lo
    return sorted_samples[lo] * (1.0 - frac) + sorted_samples[hi] * frac


def _make_stats(samples: Sequence[float]) -> SampleStats:
    ordered = tuple(sorted(samples))
    if len(samples) == 1:
        value = samples[0]
        return SampleStats(
            value, 0.0, 0.0, value, value, value, value, value, value, tuple(samples)
        )
    median = statistics.median(samples)
    return SampleStats(
        mean=statistics.mean(samples),
        stdev=statistics.stdev(samples),
        variance=statistics.pvariance(samples),
        minimum=ordered[0],
        maximum=ordered[-1],
        median=median,
        p50=median,
        p95=_percentile(ordered, 95.0),
        p99=_percentile(ordered, 99.0),
        samples=tuple(samples),
    )


def _fmt_time(seconds: float) -> str:
    if seconds >= 1.0:
        return f"{seconds:.3f}s"
    return f"{seconds * 1000:.2f}ms"


def _fmt_mean_std(stats: SampleStats) -> str:
    if stats.mean >= 1.0:
        return f"{stats.mean:.3f}±{stats.stdev:.3f}s"
    return f"{stats.mean * 1000:.2f}±{stats.stdev * 1000:.2f}ms"


def _fmt_p99(stats: SampleStats) -> str:
    return _fmt_time(stats.p99)


def _fmt_ratio(ratio: float) -> str:
    return f"{ratio:.2f}x"


def _fmt_verdict(ratio: float) -> str:
    if ratio <= 0.0:
        return "—"
    if ratio < 0.95:
        return f"cypy +{(1.0 - ratio) * 100:.0f}% (≥5% gate)"
    if ratio < 0.98:
        return f"cypy +{(1.0 - ratio) * 100:.0f}%"
    if ratio > 1.02:
        return f"baseline +{(ratio - 1.0) * 100:.0f}%"
    return "~tie"


class BenchSession:
    def __init__(self, title: str, *, n: int = N, runs: int = RUNS, warmup: int = WARMUP) -> None:
        self.title = title
        self.n = n
        self.runs = runs
        self.warmup = warmup
        self._sections: list[_Section] = []
        self._current: _Section | None = None
        self._rows: list[CompareRow] = []

    def header(self) -> None:
        print(self.title)
        print(f"{self.n:,} iterations × {self.runs} runs  (warmup {self.warmup})")
        print("ratio = mean(cypy) / mean(baseline)  (< 1.0 → cypy wins); p99 shown for tails")
        print("gate: mean ratio ≤ 0.95 (≥5% win) or ≤ 1.02 with API-clarity keep")
        print()

    def section(self, title: str) -> None:
        self._flush_section()
        self._current = _Section(title=title)
        self._sections.append(self._current)

    def compare(
        self,
        label: str,
        cy_func: Callable[..., object],
        py_func: Callable[..., object],
        *args: object,
        param: str = "",
    ) -> CompareRow:
        cy_stats = collect_stats(cy_func, *args, n=self.n, runs=self.runs, warmup=self.warmup)
        py_stats = collect_stats(py_func, *args, n=self.n, runs=self.runs, warmup=self.warmup)
        return self._record(label, param, cy_stats, py_stats)

    def compare_mutate(
        self,
        label: str,
        cy_func: Callable[..., object],
        py_func: Callable[..., object],
        template: T,
        factory: Callable[[T], T],
        *args: object,
        param: str = "",
    ) -> CompareRow:
        cy_stats = collect_mutate_stats(
            cy_func, template, factory, *args, n=self.n, runs=self.runs, warmup=self.warmup
        )
        py_stats = collect_mutate_stats(
            py_func, template, factory, *args, n=self.n, runs=self.runs, warmup=self.warmup
        )
        return self._record(label, param, cy_stats, py_stats)

    def _record(
        self,
        label: str,
        param: str,
        cy_stats: SampleStats,
        py_stats: SampleStats,
    ) -> CompareRow:
        row = CompareRow(label=label, param=param, cypy=cy_stats, baseline=py_stats)
        self._rows.append(row)
        if self._current is not None:
            self._current.rows.append(row)
        return row

    def _flush_section(self) -> None:
        if self._current is None or not self._current.rows:
            return

        print(self._current.title)
        table = TextTable(
            ("case", "cypy mean±σ", "cypy p99", "base mean±σ", "base p99", "ratio", "p99×", "verdict"),
            aligns=("left", "right", "right", "right", "right", "right", "right", "left"),
        )
        for row in self._current.rows:
            table.add(
                row.param or "—",
                _fmt_mean_std(row.cypy),
                _fmt_p99(row.cypy),
                _fmt_mean_std(row.baseline),
                _fmt_p99(row.baseline),
                _fmt_ratio(row.ratio_mean),
                _fmt_ratio(row.ratio_p99),
                _fmt_verdict(row.ratio_mean),
            )
        for line in table.render():
            print(line)
        print()

    def summary(self) -> None:
        self._flush_section()
        if not self._rows:
            return

        wins = sum(1 for row in self._rows if row.ratio_mean < 1.0)
        gate_wins = sum(1 for row in self._rows if 0.0 < row.ratio_mean <= 0.95)
        ratios = [row.ratio_mean for row in self._rows if row.ratio_mean > 0.0]
        mean_ratio = statistics.mean(ratios) if ratios else 0.0
        median_ratio = statistics.median(ratios) if ratios else 0.0

        print("─" * 72)
        print(
            f"summary: {wins}/{len(self._rows)} cypy faster  ·  "
            f"{gate_wins}/{len(self._rows)} pass ≥5% gate  ·  "
            f"mean ratio {mean_ratio:.2f}x  ·  median {median_ratio:.2f}x"
        )

        if len(self._sections) <= 1:
            print()
            return

        print()

        overview = TextTable(
            ("operation", "case", "cypy mean±σ", "p99", "ratio", "p99×", "verdict"),
            aligns=("left", "left", "right", "right", "right", "right", "left"),
        )
        for row in self._rows:
            overview.add(
                row.label,
                row.param or "—",
                _fmt_mean_std(row.cypy),
                _fmt_p99(row.cypy),
                _fmt_ratio(row.ratio_mean),
                _fmt_ratio(row.ratio_p99),
                _fmt_verdict(row.ratio_mean),
            )
        for line in overview.render():
            print(line)
        print()
