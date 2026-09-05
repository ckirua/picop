# cypy benchmarks

## Layout

| Path | Role |
|------|------|
| `_bench_util.py` | Warmup / multi-run stats / ratio tables (mean±σ, p99) |
| `cy*_bench.py` | Per-module Tier A harness |
| `tier_b/` | Tier B Cython microbenches (`*_tb.pyx` + runners) |
| `small.sh` | Run all Tier A `*_bench.py`, write `results/` |
| `results/` | Timestamped + `latest.txt` (gitignored contents) |

```bash
source .venv/bin/activate
./bench/small.sh
# or one module (Tier A):
python bench/cytuple_bench.py
# Tier B (compile + run; local — not required CI for Phase 4):
./bench/tier_b/run.sh cytuple
# or:
python -m bench.tier_b.build cytuple && python -m bench.tier_b.cytuple
```

Env (Tier A defaults): `CPY_BENCH_N` (80000), `CPY_BENCH_RUNS` (5), `CPY_BENCH_WARMUP` (0).  
Heavier Tier A: `CPY_BENCH_N=500000 CPY_BENCH_RUNS=11`.  
Tier B inner-loop count: `CPY_TIERB_N` (default **2_000_000**; falls back to `CPY_BENCH_N` when set).

## Tiers

| Tier | Baseline | Subject | Use for |
|------|----------|---------|---------|
| **A** | Plain Python (`t[i]`, `len`, `in`, `dict.get`, …) | Public `cpdef` via `bench/cy*_bench.py` | APPROVED / reject / demote public |
| **B** | Same op in a typed Cython `cdef` loop (no Python attr lookup in the hot loop) | Same public helper inside a matching `cdef` loop | Informational vs Cython emit; **does not reopen** the Tier A gate |

**Tier B harness:** `bench/tier_b/{name}_tb.pyx` + `python -m bench.tier_b.{name}`. Both sides run an N-iteration loop in Cython; Python times one full-loop call per sample. Ratio = **cypy_loop / cython_baseline_loop**. Anti-DCE/LICM: `_sink.pxi` opaque identity + volatile sink. Build artifacts (`*.so`, `*.c`) are gitignored — compile locally before merge when adding results.

**Tier B n/a:** cimport-only / surface-none modules, or unfair I/O (document one rationale line in the tracker).

Decision gate (see [`docs/README.md`](../docs/README.md)) — **Tier A only**:

- **Primary metric:** mean wall time; **ratio = cypy / baseline**
- **APPROVED (perf):** primary scenario **ratio ≤ 0.95**
- **APPROVED (API):** ratio ≤ 1.02 with API-clarity note
- **Evidence:** paste the timed table + experiment conclusions into **`docs/modules/NNN_cy{name}.md`** (not separate RESULTS/NOTES files)
- **Tier B:** paste under `### Tier B (Cython baseline)` inside Bench results (or sibling `## Tier B results`); keep Tier A tables intact

## Primary scenarios

| Module | Primary case |
|--------|----------------|
| cytuple | `tget` index=0 |
| cybytes | `bcontains` multi-byte hit (`b"ab" in b"abcabc"`) |
| cybytearray | `balen` small |
| cyarray | `aylen` small |
| cydict | `dget` hit `key='symbol'` |
