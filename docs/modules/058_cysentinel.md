# cysentinel

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.sentinelobject.h` (CPython **3.15+**) |
| Sources | `src/picop/cysentinel.pxd`, `src/picop/cysentinel.pyx`, `src/picop/cysentinel.pyi`, `src/picop/cysentinel_shim.h` |
| Surface | public + cimport |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

CPython 3.15 adds sentinel instances with their own builtin type and C API.
The module exposes two recognition checks, construction, and access to that
static type. On CPython 3.14 the checks remain importable and return false;
construction/type access report the documented unsupported-version behavior.
The constructor accepts explicit module and repr values; unlike the builtin
caller-facing constructor, its module default is `None` rather than inferred.

## Inventory

Complete `PySentinel_*` surface from `cpython/sentinelobject.h` and picop's
four-helper module API. No unrelated sentinel implementation details are
wrapped.

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| `PySentinel_Type` | C-API | static type object | `sentinel_type` | Static builtin sentinel type; no subtypes |
| `PySentinel_Check(obj)` | C-API | macro | `sentinel_check` | Recognizes sentinel instances; with no subtypes equivalent to exact check |
| `PySentinel_CheckExact(obj)` | C-API | macro | `sentinel_check_exact` | Exact-type check |
| `PySentinel_New(name, module, repr)` | C-API | function | `sentinel_new` | New reference; picop accepts optional module/repr as `None` |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| `sentinel_check` | APPROVED | Tier A 0.31–0.82x; Tier B 0.10x hit / 0.05x miss |
| `sentinel_check_exact` | APPROVED | Tier A 0.28–0.52x; Tier B 0.12–0.13x |
| `sentinel_new` | APPROVED | Tier A 0.82x mean (allocation-sensitive; earlier pass 0.95x); direct constructor kept for explicit module/repr |
| `sentinel_type` | APPROVED | Tier A 0.54x; exposes the C type accessor |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 0 |
| Last pass | 2026-11-05 — full inventory, Tier A try-all + depth probes, Tier B checks |
| Next action | None; no subsequent queue order is inferred |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| `sentinel_check` | C type check beats Python `isinstance` | `bench/cysentinel_bench.py` | Tier A hit 0.82x, miss 0.31x; Tier B 0.10x / 0.05x | APPROVED | 0 |
| `sentinel_check_exact` | Exact C type check beats Python type comparison | same | Tier A hit 0.52x, miss 0.28x; Tier B 0.12x / 0.13x | APPROVED | 0 |
| `sentinel_new` | Direct C constructor improves construction | same | 0.82x mean, gate passed (earlier pass 0.95x, allocation-noise sensitive) | APPROVED | 0 |
| `sentinel_type` | C type accessor is cheaper than Python lookup | same | 0.54x, measured with the direct shim accessor | APPROVED | 0 |

## Bench notes

- Harness: [`bench/cysentinel_bench.py`](../../bench/cysentinel_bench.py) — see [`bench/BENCH.md`](../../bench/BENCH.md)
- Tier B harness: [`bench/tier_b/cysentinel.py`](../../bench/tier_b/cysentinel.py) (`cysentinel_tb.pyx`)
- **Mandatory:** paste **Bench results** + **Experiment conclusions** into **this file** after every measuring pass — **no skip** (PR-only is not enough)
- Gate: [`docs/README.md`](../README.md) (mean ratio ≤ 0.95; cimport demote allowed)
- Env: CPython 3.15.0rc2, Linux x86_64, GIL build; Tier A N=80,000 × RUNS=5; Tier B timed harness results as recorded below

## Bench results

### Tier A (public helper vs plain Python)

| operation | case | picop mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| `sentinel_check` | hit | 3.54±1.04ms | 4.55ms | 0.82x | 1.03x | APPROVED |
| `sentinel_check` | miss | 2.10±0.05ms | 2.14ms | 0.31x | 0.25x | APPROVED |
| `sentinel_check_exact` | hit | 2.10±0.11ms | 2.29ms | 0.52x | 0.57x | APPROVED |
| `sentinel_check_exact` | miss | 2.52±0.94ms | 4.12ms | 0.28x | 0.35x | APPROVED |
| `sentinel_new` | construct | 8.84±0.87ms | 10.07ms | 0.82x | 0.65x | APPROVED |
| `sentinel_type` | accessor | 1.94±0.03ms | 1.99ms | 0.54x | 0.54x | APPROVED |

6/6 cases were faster by mean and 6/6 passed the mean ≤0.95 gate (mean ratio
0.55x, median 0.53x). The two hit cases are allocation/attribute-noise dominated
and vary between runs (an earlier pass measured 0.55x / 0.49x); every pass kept
both helpers comfortably inside the gate.

### Tier B (cdef loop vs typed Cython baseline)

| operation | case | picop mean±σ | baseline mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----------------|-------|------|------|
| `sentinel_check` | hit | 2.98±0.35ms | 30.32±8.54ms | 0.10x | 0.08x | faster |
| `sentinel_check` | miss | 2.73±0.02ms | 52.84±0.38ms | 0.05x | 0.05x | faster |
| `sentinel_check_exact` | hit | 2.66±0.04ms | 21.45±0.41ms | 0.12x | 0.12x | faster |
| `sentinel_check_exact` | miss | 2.69±0.06ms | 21.40±0.15ms | 0.13x | 0.13x | faster |

The Tier B baseline is dynamically imported Python type-check logic, not an
identical C macro baseline; interpret these ratios accordingly. Re-runs of the
same harness land between 0.05x and 0.13x depending on runner load.

## Experiment conclusions

- **Try-all.** All four helpers were measured in both tiers. The two check
  helpers are fast in both tiers; `sentinel_type` and `sentinel_new` both passed
  the Tier A gate in the final pass (constructor 0.82x; an earlier pass measured
  0.95x, so the constructor win is real but allocation-noise sensitive).
- **Subtype semantics.** The sentinel type has no subtypes, so check and exact
  check recognize the same instances. Keep both documented helpers for their
  corresponding C API semantics and caller clarity.
- **Constructor contract.** picop's optional `module` defaults explicitly to
  `None`; it does not infer the caller's module as the builtin constructor may.
  Inputs cross a C-string UTF-8 boundary: embedded NUL is rejected, and UTF-8
  surrogate encoding errors propagate. The returned sentinel is a new owned
  object reference.
- **Depth and ownership.** Check helpers inspect the object's type and do not
  mutate it. Constructor output is independently owned by the caller. Results
  describe the measured CPython 3.15 GIL build only; no free-threading or other
  version performance/safety conclusion is inferred from these runs.
- **Accessor implementation choice.** `sentinel_type()` returns a fresh
  reference to `PySentinel_Type` through the shim rather than a cached Python
  global lookup; the recorded 0.54x Tier A ratio is for that direct accessor.
  Callers that only need a type test should use the check helpers instead of
  comparing against the accessor result.
- **Tier B interpretation.** The comparison uses dynamically imported Python
  type-check code, not a direct equivalent of the static C pointer/macro path;
  the large ratios should not be represented as a C-macro-vs-Cython result.

## Done when

- [x] Full inventory vs mapped include (or declared custom surface)
- [x] Every row has workflow status
- [x] Lifecycle + next action filled
- [x] APPROVED / APPROVED (cimport) rows have decision-log evidence
- [x] REJECTED rows have policy or measured why
- [x] Present measuring: try-all **and** depth checklist in **this tracker's** Experiment conclusions (**no skip**)
- [x] **Bench results** table filled in **this file** (not only PR)
- [x] Public PEP 257 one-liners in `cysentinel.pyi`; `.pxd` lean — [`PIPELINE.md`](../PIPELINE.md)
