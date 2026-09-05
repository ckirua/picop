# cygc

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `Python.h` GC (`PyGC_*`) — no Cython `cpython.gc` |
| Sources | `src/cypy/cygc.pxd`, `cygc.pyx`, `cygc.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

GC enable/disable/is-enabled/collect for tuning scripts and extension control.

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| gc_is_enabled / gc_is_enabled_c | cypy | cpdef/cdef | public / cimport | `PyGC_IsEnabled` |
| gc_enable / gc_enable_c | cypy | cpdef/cdef | public / cimport | `PyGC_Enable` |
| gc_disable / gc_disable_c | cypy | cpdef/cdef | public / cimport | `PyGC_Disable` |
| gc_collect / gc_collect_c | cypy | cpdef/cdef | public / cimport | `PyGC_Collect` |
| PyObject_GC_Track/UnTrack/New* | C-API | tried | — | type plumbing; REJECTED |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| gc_is_enabled | APPROVED | primary **0.94x** |
| gc_enable / gc_disable | APPROVED | round-trip **0.71x** |
| gc_collect | APPROVED | API mirror; one-shot ~parity with `gc.collect` (not N-looped) |
| Track/New* | REJECTED | not tuning surface |

## Lifecycle

| Field | Value |
|-------|--------|
| Freeze | **1.0 Core** — public + documented cimport; see COVERAGE § 1.0 freeze |
| Iteration | 1 |
| Last pass | 2026-07-21 — Phase 4 Tier B (Cython baseline) |
| Next action | — |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| gc_is_enabled | Beat gc.isenabled | `bench/cygc_bench.py` | **0.94x** | APPROVED | 1 |
| enable/disable | Beat gc module | same | **0.71x** | APPROVED | 1 |
| gc_collect | Mirror | one-shot smoke | ~parity | APPROVED | 1 |

## Bench notes

- Harness: [`bench/cygc_bench.py`](../../bench/cygc_bench.py)
- **Do not** N-loop `gc_collect` — full collections dominate wall time
- Env: CPython 3.14.6 · Linux x86_64 · GIL on · N=80000 RUNS=5

## Bench results

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| gc_is_enabled | enabled? | 0.78±0.01ms | 0.79ms | 0.94x | 0.94x | pass |
| gc_disable+enable | roundtrip | 2.24±0.16ms | 2.48ms | 0.71x | 0.75x | pass |
| gc_collect | one-shot | ~0.8ms | — | ~parity | — | smoke |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cygc.py`](../../bench/tier_b/cygc.py) · `cygc_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| gc_is_enabled | flag read | 0.81±0.01ms | 0.82ms | 0.78±0.00ms | **1.05x** | 1.04x | baseline faster |

**Tier B takeaway:** `gc_is_enabled` **1.05x** vs `PyGC_IsEnabled` — thin cpdef; collect/enable stay unfair for Tier B loops.

## Experiment conclusions

**Tier B:** `gc_is_enabled` **1.05x** vs `PyGC_IsEnabled` — thin cpdef; collect/enable stay unfair for Tier B loops.

- **Why win:** thin `PyGC_*` vs `gc` module attribute lookup.
- **collect:** must stay out of tight loops; one-shot ~same cost as `gc.collect` (same C entry).
- **Free-threaded / GIL:** GC enable state is process-global; disable around stop-the-world sensitive sections carefully. Track/UnTrack left unwrapped (type authors use Cython/`Python.h` directly).

## Done when

- [x] Full PyGC_* inventory
- [x] Bench results + Experiment conclusions
- [x] Public `.pyi` one-liners
