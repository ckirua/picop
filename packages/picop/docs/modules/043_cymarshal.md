# cymarshal

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.marshal` |
| Sources | `src/cypy/cymarshal.pxd`, `.pyx`, `.pyi` |
| Surface | public |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

In-memory marshal dumps/loads for Cython.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| marshal_dumps / loads | public | via ``marshal.h`` |
| FILE* Read/Write* | — | REJECTED (FILE*) |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| dumps/loads | APPROVED | works after ``marshal.h`` include |
| FILE* | REJECTED | FILE* surface |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 2 |
| Last pass | 2026-07-21 — Phase 4 Tier B |
| Next action | — |

## Bench notes

- Harness: [`bench/cymarshal_bench.py`](../../bench/cymarshal_bench.py)

## Bench results

Harness: [`bench/cymarshal_bench.py`](../../bench/cymarshal_bench.py) · tier A · CPython 3.14 · N=80_000

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| marshal_dumps | dict | **1.01x** | APPROVED (API) |
| marshal_loads | bytes | **0.94x** | APPROVED |
| FILE* Read/Write | — | n/a | REJECTED ABI (FILE*) |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cymarshal.py`](../../bench/tier_b/cymarshal.py) · `cymarshal_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=200_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| marshal_dumps | dict | 19.52±0.16ms | 19.75ms | 19.71±0.16ms | **0.99x** | 0.99x | ~tie |

**Tier B takeaway:** primary `marshal_dumps` **0.99x** vs typed Cython baseline (dict).


## Experiment conclusions

**Tier B:** `marshal_dumps` **1.01x** vs marshal.dumps — ~parity (allocating).

| Topic | Finding |
|-------|---------|
| Why ~tie | Same marshal codec as `marshal.dumps/loads`; thin wrapper overhead |
| ABI | Must `cdef extern from "marshal.h"` — `Python.h`-only decls crash at call |
| Safety / ownership | Dumps returns owned bytes; loads returns owned object; FILE* surface REJECTED |
| Scale | Payload size dominates; ratios stay near 1.0x across small/medium objects |
| Prefer | In-memory dumps/loads for Cython; leave FILE* to C embedding code |

## Done when

- [x] Try-all + depth + benches + `.pyi` + include fix
