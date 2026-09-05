# cytime

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.time` |
| Sources | `src/cypy/cytime.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

CPython ``PyTime_*`` clocks for Cython (not deferred to cycel.time).

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| time_wall / time_monotonic / time_perf_counter | public | seconds as float; prefer `time_wall` |
| time_time | cimport impl | 0.3: cdef-only; prefer `time_wall` |
| *_raw / as_seconds | cimport | ``PyTime_t`` |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| time_* public | APPROVED | see benches |
| raw PyTime_t | APPROVED (cimport) | integer ticks |

## Lifecycle

| Field | Value |
|-------|--------|
| Freeze | **Provisional (Runtime)** after 1.0 — not Core; may evolve under minors |
| Iteration | 1 |
| Last pass | 2026-07-21 — Phase 4 Tier B |
| Next action | — |

## Bench notes

- Harness: [`bench/cytime_bench.py`](../../bench/cytime_bench.py)

## Bench results

Harness: [`bench/cytime_bench.py`](../../bench/cytime_bench.py) · tier A · CPython 3.14 · N=80_000

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| time_time | wall | **2.00x** | REJECTED public hot (scale lose) |
| time_monotonic | mono | **1.01x** | APPROVED (API) |
| time_perf_counter | perf | **0.98x** | APPROVED (API) |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cytime.py`](../../bench/tier_b/cytime.py) · `cytime_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=100_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| time_time | clock | 2.08±0.01ms | 2.09ms | 2.20±0.07ms | **0.94x** | 0.90x | cypy faster |

**Tier B takeaway:** primary `time_time` **0.94x** vs typed Cython baseline (clock).


## Experiment conclusions

**Tier B:** `time_time` **0.97x** vs `time.time` — ~parity.

| Topic | Finding |
|-------|---------|
| Why wall loses | Extra float convert / wrapper vs already-thin `time.time`; **2.00x** — demote as hot path |
| Why mono/perf ~tie | Same `PyTime_*` clocks as stdlib; wrapper ≈ noise |
| Scale | Clock read cost is fixed; no size crossover — loss is pure call overhead |
| ABI / ownership | Raw `PyTime_t` helpers stay cimport for hot Cython without float convert |
| Prefer | Public as API bridge; hot loops use raw ticks under GIL-friendly cdef |

## Done when

- [x] Try-all + depth + benches + `.pyi`

### Stub visibility (2026-08-02)

- Stub-hidden (Tier A `>1.02x`): `time_wall`. Still `cpdef`.

