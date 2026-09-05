# cycodecs

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.codecs` |
| Sources | `src/cypy/cycodecs.pxd`, `.pyx`, `.pyi` |
| Surface | public |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Codec encode/decode and registry helpers for Cython.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| codec_known / encode / decode / encoder / decoder / incremental* / stream* / error handlers / register* | public | full registry surface |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| codec_known / encode / decode | APPROVED / API | see benches |
| remaining registry helpers | APPROVED (API) | completeness / cheap aliases |

## Lifecycle

| Field | Value |
|-------|--------|
| Freeze | **Provisional (Runtime)** after 1.0 — not Core; may evolve under minors |
| Iteration | 1 |
| Last pass | 2026-07-21 — Phase 4 Tier B |
| Next action | — |

## Decision log

| Function | Decision | Iteration |
|----------|----------|-----------|
| known/encode/decode | APPROVED/API | 1 |
| error handlers / streams | APPROVED (API) | 1 |

## Bench notes

- Harness: [`bench/cycodecs_bench.py`](../../bench/cycodecs_bench.py)

## Bench results

Harness: [`bench/cycodecs_bench.py`](../../bench/cycodecs_bench.py) · tier A · CPython 3.14 · N=80_000

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| codec_encode | utf-8 short | **0.52x** | APPROVED |
| codec_decode | utf-8 short | **1.29x** | APPROVED (API) |
| codec_encode | utf-8 long | **1.54x** | demoted scale loss |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cycodecs.py`](../../bench/tier_b/cycodecs.py) · `cycodecs_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| codec_known | utf-8 | 61.92±0.15ms | 62.16ms | 52.15±1.41ms | **1.19x** | 1.17x | baseline faster |

**Tier B takeaway:** primary `codec_known` **1.19x** vs typed Cython baseline (utf-8).


## Experiment conclusions

**Tier B:** `codec_known` **1.25x** vs codecs registry path — keep; informational.

| Topic | Finding |
|-------|---------|
| Why short encode wins | Thin C registry entry vs `str.encode` method lookup on tiny payloads |
| Scale | Long strings flip to **1.54x** — codec body dominates; wrapper overhead no longer helps |
| Why decode loses | Same registry path; CPython decode already specialized — keep as API bridge |
| ABI / safety | NULL errors → strict; registry helpers are cheap siblings for Cython completeness |
| Prefer | Hot short encode via cypy; large payloads prefer builtin `.encode`/`.decode` |

## Done when

- [x] Try-all + depth + benches + `.pyi`

### Ops remaining inventory (Tier A)

Harnesses: [`bench/cyaccessors_inventory_bench.py`](../../bench/cyaccessors_inventory_bench.py) / [`bench/cyruntime_inventory_bench.py`](../../bench/cyruntime_inventory_bench.py). See [`OPS_INVENTORY.md`](../OPS_INVENTORY.md) + [`OPS_INVENTORY_TIERB.md`](../OPS_INVENTORY_TIERB.md) for status / Tier B n/a.

### Stub visibility (2026-08-02)

- Stub-hidden (Tier A `>1.02x`): `codec_encode`, `codec_decode`. Still `cpdef`.

