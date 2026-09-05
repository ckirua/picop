# cyconversion

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.conversion` |
| Sources | `src/cypy/cyconversion.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

Locale-independent string↔double and case-insensitive C compares.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| conv_string_to_double / stricmp / strnicmp | public | |
| conv_double_to_string | cimport | caller frees |
| snprintf | — | REJECTED (varargs buffer) |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| string_to_double / stricmp* | APPROVED | see benches |
| double_to_string | APPROVED (cimport) | PyMem_Free required |
| snprintf | REJECTED | varargs buffer API |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-07-21 — Phase 4 Tier B |
| Next action | — |

## Bench notes

- Harness: [`bench/cyconversion_bench.py`](../../bench/cyconversion_bench.py)

## Bench results

Harness: [`bench/cyconversion_bench.py`](../../bench/cyconversion_bench.py) · tier A · CPython 3.14 · N=80_000

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| conv_string_to_double | ascii | **0.76x** | APPROVED |
| conv_stricmp | equal | **0.37x** | APPROVED |
| conv_strnicmp | prefix | **0.37x** | APPROVED |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cyconversion.py`](../../bench/tier_b/cyconversion.py) · `cyconversion_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| conv_string_to_double | pi | 27.27±0.42ms | 27.97ms | 47.95±0.05ms | **0.57x** | 0.58x | cypy faster |
| conv_stricmp | icmp | 2.68±0.02ms | 2.70ms | 50.17±1.00ms | **0.05x** | 0.05x | cypy faster |

**Tier B takeaway:** primary `conv_string_to_double` **0.57x** vs typed Cython baseline (pi).


## Experiment conclusions

**Tier B:** `conv_string_to_double` **0.59x** / `conv_stricmp` **0.10x** vs libc/Python baselines.

| Topic | Finding |
|-------|---------|
| Why win | Locale-independent C parsers/compares beat `float()` / Python `.lower()` paths |
| Ownership / safety | `double_to_string` allocates — caller must `PyMem_Free`; cimport only |
| ABI | snprintf REJECTED (varargs buffer); string_to_double rejects whitespace unlike `float()` |
| Scale | Cost scales with string length for icmp/nicmp; no crossover vs Python for short keys |
| Prefer | Hot ASCII numeric/compare in Cython; keep alloc-returning APIs cdef |

## Done when

- [x] Try-all + depth + benches + `.pyi`
