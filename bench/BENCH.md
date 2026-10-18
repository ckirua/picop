# picop benchmarks

## Layout

| Path | Role |
|------|------|
| `_bench_util.py` | Warmup / multi-run stats / ratio tables (mean±σ, p99) |
| `cy*_bench.py` | Per-module Tier A harness |
| `cycall_bench.py` | Call-helper Tier A harness; direct-call baselines |
| `tier_b/` | Tier B Cython microbenches (`*_tb.pyx` + runners) |
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

**3.0 namespace:** runnable harnesses import and cimport `picop`. Historical
`cypy` benchmark-function names, result labels, and the UUID JSON suite ID
`cypy.uuid` remain measurement-format identifiers, not import compatibility.
Smoke-sized loop overrides verify executability only; they are not performance
acceptance evidence and must not refresh measured baselines.

## Tiers

| Tier | Baseline | Subject | Use for |
|------|----------|---------|---------|
| **A** | Plain Python (`t[i]`, `len`, `in`, `dict.get`, …) | Public `cpdef` via `bench/cy*_bench.py` | APPROVED / reject / demote public |
| **B** | Same op in a typed Cython `cdef` loop (no Python attr lookup in the hot loop) | Same public helper inside a matching `cdef` loop | Informational vs Cython emit; **does not reopen** the Tier A gate |

**Tier B harness:** `bench/tier_b/{name}_tb.pyx` + `python -m bench.tier_b.{name}`. Both sides run an N-iteration loop in Cython; Python times one full-loop call per sample. Ratio = **picop_loop / cython_baseline_loop**. Anti-DCE/LICM: `_sink.pxi` opaque identity + volatile sink. Build artifacts (`*.so`, `*.c`) are gitignored — compile locally before merge when adding results.

**Tier B n/a:** cimport-only / surface-none modules, or unfair I/O (document one rationale line in the tracker).

Decision gate (see [`docs/README.md`](../docs/README.md)) — **Tier A only**:

- **Primary metric:** mean wall time; **ratio = picop / baseline**
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
| cycall | `call_noargs`, `call_onearg`, `call_twoargs` vs actual direct invocation |
| cybuffer | `buf_itemsize`, `buf_nbytes`, `buf_ndim`, `buf_readonly` over live buffer exporters |
| cymemoryview | Metadata helpers over retained views, including non-byte and multidimensional views |

## Native UUID reference

The UUID harness is separate from Tier A/B:
[`scripts/benchmarks/uuid/bench.py`](../scripts/benchmarks/uuid/bench.py).
The JSON suite ID `cypy.uuid` and `*_cached` operation labels are retained
measurement-format identifiers, not imports or claims of private lazy caches.

[`baseline-native-i7-6700-cpython315.json`](../scripts/benchmarks/uuid/results/baseline-native-i7-6700-cpython315.json)
records the native UUID implementation installed from the portable
`picop==3.0.0rc1` PyPI sdist, not a `CPY_NATIVE=1` build. It includes all 60
samples per operation, the source commit/archive digest, CPU, runtime/compiler,
GIL mode, system and sampling metadata. Only `uuid4` and `uuid4_bytes` are
gated; the other seven operations are informational.

Reference conditions: Intel i7-6700, CPython **3.15.0rc2**, pyperf **2.10.0**,
Linux x86_64, GIL enabled, manager and workers pinned to CPU **2**, 20 processes
× 3 values, 1 warmup, minimum value time 0.1 seconds. The CPU's SMT sibling is
6; the observed governor was `powersave`, with turbo enabled. No system tuning
was applied. pyperf emitted stability warnings; these results do not establish
sub-percent precision or a speedup over a different implementation.

Run with an otherwise idle machine and the same installed build/runtime:

```bash
taskset -c 2 python scripts/benchmarks/uuid/bench.py \
  --affinity 2 --output candidate.json
python scripts/benchmarks/uuid/check_baseline.py candidate.json \
  --baseline scripts/benchmarks/uuid/results/baseline-native-i7-6700-cpython315.json
```

The gate checks medians and the result schema, **not environment equivalence**.
Inspect the recorded CPU, ABI/GIL state, Python/compiler, build flags, affinity
and sampling metadata before using a reference. This profile is not a baseline
for other hardware, another Python build, a free-threaded ABI or a tuned build.

The default [`baseline.json`](../scripts/benchmarks/uuid/results/baseline.json)
is unchanged: it records the historical Core Ultra 7 265 / CPython 3.14.6 run.
Omitting `--baseline` still checks that historical reference. Its absolute
numbers are not comparable to the i7-6700 measurements; a failure there must
not be hidden by replacing the reference or increasing the unchanged **25%**
regression budget. New comparisons must not overwrite a measured reference.

### Independent reference check (2026-10-18)

A second full-default run used the same installed RC1 build and identical
recorded environment; it did not generate or replace the reference.
[`validation-native-i7-6700-cpython315.json`](../scripts/benchmarks/uuid/results/validation-native-i7-6700-cpython315.json)
retains all 60 samples for each of the nine operations.

| Gated operation | Reference median (ns) | Independent median (ns) | Change | 25% gate |
|---|---:|---:|---:|---|
| `uuid4` | 110.630 | 111.688 | +0.96% | PASS |
| `uuid4_bytes` | 49.208 | 48.148 | −2.15% | PASS |

Both runs emitted pyperf stability warnings. This establishes a reproducible
host-specific regression reference within the existing budget, not a UUID
speedup or evidence that every individual sample is stable. The historical
default gate still fails on this different CPU/runtime, as expected; that
failure was not converted into a passing result by modifying its baseline.

