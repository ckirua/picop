# cydescr

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.descr` |
| Sources | `src/cypy/cydescr.pxd`, `.pyx`, `.pyi` |
| Surface | public |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Data-descriptor check. `PyDescr_NewWrapper` needs C `wrapperbase*` — REJECTED as public/cypy wrapper (use Cython Includes directly if needed).

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| descr_is_data | public | |
| NewWrapper / wrapperbase | — | REJECTED (C-only struct API) |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| descr_is_data | APPROVED | beats hasattr heuristic |
| NewWrapper | REJECTED | requires wrapperbase* / not useful as cpdef |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-07-21 — Phase 4 Tier B |
| Next action | — |

## Decision log

| Function | Decision | Iteration |
|----------|----------|-----------|
| IsData | APPROVED | 1 |
| NewWrapper | REJECTED | 1 |

## Bench notes

- Harness: [`bench/cydescr_bench.py`](../../bench/cydescr_bench.py)

## Bench results

Harness: [`bench/cydescr_bench.py`](../../bench/cydescr_bench.py) · tier A · CPython 3.14 · N=80_000

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| descr_is_data | property | **0.28x** | APPROVED |
| descr_is_data | method | **0.31x** | APPROVED |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cydescr.py`](../../bench/tier_b/cydescr.py) · `cydescr_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| descr_is_data | property | 2.97±0.09ms | 3.10ms | 11.38±0.36ms | **0.26x** | 0.26x | cypy faster |

**Tier B takeaway:** primary `descr_is_data` **0.26x** vs typed Cython baseline (property).


## Experiment conclusions

**Tier B:** `descr_is_data` **0.27x** vs hasattr `__set__`.

| Topic | Finding |
|-------|---------|
| Why win | Reads descriptor flags in C; `hasattr(__set__)` walks the type dict and can lie for non-data descrs |
| Scale | Flag test is O(1); Python heuristic cost grows with MRO / attribute search |
| ABI / safety | `PyDescr_NewWrapper` needs `wrapperbase*` — C-only; REJECTED as public |
| Subtype | Works for builtin property/method descriptors; custom descr subtypes still consult `tp_descr_set` |
| Prefer | Use `descr_is_data` in Cython type tooling; keep NewWrapper in Cython Includes |

## Done when

- [x] Try-all + depth + benches + `.pyi`
