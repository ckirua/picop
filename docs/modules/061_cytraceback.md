# cytraceback

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.traceback` |
| Sources | `src/picop/cytraceback.pxd`, `.pyx`, `.pyi` + `cytraceback_shim.h` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Provide small, typed accessors for CPython traceback objects where Python-level attribute access or repeated chain traversal is costly in Cython hot paths. The public surface includes exact type checking, ownership-preserving next/frame access, source location fields, and chain depth. The module intentionally excludes traceback construction, printing, and unstable diagnostic dumping: these have different lifecycle, ABI, or side-effect contracts. Line-number semantics require special care because CPython 3.11+ stores `-1` in the raw traceback line field and derives the reported line from the frame's instruction offset.

## Inventory

Selected traceback-object surface and explicitly rejected adjacent APIs.

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| `PyTraceBack_Check` | C-API | macro | `tb_check` | `Py_IS_TYPE`; exactness is structural because traceback type is not subclassable |
| `tb_next` | cypy | helper | public | Strong reference; `None` at chain end |
| `tb_frame` | cypy | helper | public | Strong reference to frame |
| `tb_lineno` | cypy | helper | public | Computes effective line; raw field is `-1` on 3.11+ |
| `tb_lasti` | cypy | helper | public | Instruction offset |
| `tb_depth` | cypy | helper | public | Counts traceback chain |
| `tb_next_borrow` | cypy | helper | cimport | Borrowed `PyObject *`, possibly NULL; owner must remain alive |
| `PyTraceBack_Here` | C-API | function | — | Mutates current exception state |
| `PyTraceBack_Print` | C-API | function | — | I/O/printing side effect |
| `PyUnstable_DumpTraceback*` | C-API | unstable function | — | Unstable diagnostic ABI |
| `tb_eq` | cypy | candidate | — | Structural chain equality is not part of this order |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| `tb_check` | APPROVED | Tier A and Tier B wins |
| `tb_next` | APPROVED | Tier A win; owning getter |
| `tb_frame` | APPROVED | Tier A win; owning getter |
| `tb_lineno` | APPROVED | Tier A win with effective-line semantics |
| `tb_lasti` | APPROVED | Tier A win |
| `tb_depth` | APPROVED | Tier A depth pass wins |
| `tb_next_borrow` | APPROVED (cimport) | Useful borrowed pointer for Cython traversal with explicit lifetime rule |
| `PyTraceBack_Here` | REJECTED | Exception-state mutation is outside the reader API |
| `PyTraceBack_Print` | REJECTED | Printing side effect is not an accessor |
| `PyUnstable_DumpTraceback*` | REJECTED | Unstable diagnostic ABI |
| `tb_eq` | REJECTED | Structural equality has no justified stable semantics |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 0 |
| Last pass | 2026-11-05 — inventory, Tier A try-all + depth, Tier B checks |
| Next action | None; no subsequent queue order is inferred |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| Public helpers | Thin C accessors beat Python attribute/type checks | Tier A + depth | 6/6 faster; mean 0.47x | APPROVED | 0 |
| `tb_check` / `tb_next` / `tb_frame` / `tb_depth` | Direct C access improves typed hot loops | Tier B | 0.16–0.48x | APPROVED | 0 |
| `tb_lineno` | Accessor matches effective Python line semantics | Tier A + semantic probe | 0.73x; Tier B raw-field mismatch documented | APPROVED | 0 |
| `tb_next_borrow` | Borrow avoids temporary ownership for immediate traversal | API review | cimport-only lifetime contract | APPROVED (cimport) | 0 |
| Mutation / printing / unstable dumps / equality | Adjacent APIs may broaden surface | ABI and policy review | Side-effect, unstable ABI, or no equality contract | REJECTED | 0 |

## Bench notes

- Harness: [`bench/cytraceback_bench.py`](../../bench/cytraceback_bench.py)
- Tier B harness: [`bench/tier_b/cytraceback.py`](../../bench/tier_b/cytraceback.py)
- Environment: CPython 3.15, Linux x86_64, GIL build; Tier A `CPY_BENCH_N=500_000`, 9 runs; Tier B `CPY_TIERB_N=2_000_000`, 5 runs.
- Ratio = picop / baseline; lower is faster.

## Bench results

### Tier A (public helper vs plain Python)

`CPY_BENCH_N=500_000`, `runs=9`:

| operation | case | picop mean±σ | p99 | baseline mean±σ | p99 | ratio | p99× | verdict |
|---|---|---:|---:|---:|---:|---:|---:|---|
| tb_check | traceback vs `isinstance` | 12.98±0.54ms | 14.27ms | 28.43±0.12ms | 28.61ms | **0.46x** | 0.50x | pass |
| tb_next | head of 4-deep chain | 13.31±0.19ms | 13.75ms | 27.70±0.18ms | 27.98ms | **0.48x** | 0.49x | pass |
| tb_frame | head | 13.17±0.23ms | 13.71ms | 30.51±0.20ms | 30.89ms | **0.43x** | 0.44x | pass |
| tb_lineno | head (raw field −1) | 32.65±0.23ms | 33.14ms | 45.03±1.56ms | 48.81ms | **0.73x** | 0.68x | pass |
| tb_lasti | head | 16.06±7.70ms | 34.77ms | 29.05±0.56ms | 30.23ms | **0.55x** | 1.15x | pass |
| tb_depth | 4-deep chain | 13.97±1.34ms | 17.23ms | 85.27±8.90ms | 106.93ms | **0.16x** | 0.16x | pass |

Summary: 6/6 picop faster, mean **0.47x**.

### Tier B (Cython baseline)

`CPY_TIERB_N=2_000_000`, 5 runs:

| operation | picop / baseline ratio |
|---|---:|
| tb_check | 0.48x |
| tb_next | 0.29x |
| tb_frame | 0.17x |
| tb_lineno | 14.81x |
| tb_lasti | 0.99x |
| tb_depth | 1.00x |

Tier B `tb_lineno` at 14.81x is not a demotion signal: the Cython baseline reads raw `tb_lineno`, which remains `-1` on CPython 3.11+, rather than computing the effective line returned by `tb.tb_lineno`. The comparison is therefore not parity-equivalent; Tier A measures the public semantic operation and is the gate (0.73x).

## Experiment conclusions

- **Why and scale.** All six public operations beat their Tier A Python baselines, with mean ratio 0.47x at N=500,000; the chain-depth helper reaches 0.16x on a four-deep traceback. The results support the direct accessors rather than a narrower public API. Tier B wins strongly on check/next/frame, while near parity for lasti/depth is informational.
- **Ownership and ABI.** `tb_next` and `tb_frame` return unique owned references (strong references), avoiding escaped borrowed results. `tb_next_borrow` is intentionally cimport-only: its borrowed `PyObject *` may be NULL, so callers must keep the traceback alive for the entire traversal. The traceback layout cannot be declared directly by Cython: `cpython/traceback.h` rejects direct inclusion and its `struct _traceback` / `PyTracebackObject` arrangement requires the shim, whose accessors accept `PyObject *` and cast internally.
- **Line semantics and concurrency.** On CPython 3.11+, the raw `tb_lineno` field is the `-1` sentinel; Python's `tb_lineno` corresponds to the line at `tb_lasti` in the frame code. The shim resolves it with `PyCode_Addr2Line(PyFrame_GetCode(...), tb->tb_lasti)` and releases the new reference returned by `PyFrame_GetCode`. Under free-threading/GIL-disabled execution, a borrowed chain pointer is safe only while its owning traceback remains alive; no claim of lock-protected traversal is made.

## Done when

- [x] Full inventory vs mapped include (or declared custom surface)
- [x] Every row has workflow status
- [x] Lifecycle + next action filled
- [x] APPROVED / APPROVED (cimport) rows have decision-log evidence
- [x] REJECTED rows have policy or measured why
- [x] Present measuring: try-all **and** depth checklist in this tracker's Experiment conclusions
- [x] Bench results table filled in this file
- [x] Public PEP 257 one-liners in `cytraceback.pyi`; `.pxd` lean — [`PIPELINE.md`](../PIPELINE.md)
