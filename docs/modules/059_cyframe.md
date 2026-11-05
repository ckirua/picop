# cyframe

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.frame` |
| Sources | `src/picop/cyframe.*` |
| Surface | public + cimport |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

Expose safe, thin readers for CPython frame objects for diagnostics, tracing,
and Cython call paths. The public surface follows the stable `PyFrame_*`
accessors without constructing frames or reaching into interpreter internals.
Python `frame` objects cannot be subclassed, so `PyFrame_Check` is already an
exact check and has no useful exact-check sibling. Accessors preserve CPython
semantics rather than materializing or coercing returned values.

## Inventory

Complete relevant `PyFrame_*` surface for the supported public readers and
explicit cimport-only low-level entries. Deprecated no-op and private internal
frame APIs are recorded as rejected in workflow decisions.

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| `PyFrame_Check` | C-API | macro | `frame_check` | Exact because frame is unsubclassable |
| `PyFrame_GetLineNumber` | C-API | function | `frame_lineno` | Integer line number |
| `PyFrame_GetLasti` | C-API | function | `frame_lasti` | Already scaled by `sizeof(_Py_CODEUNIT)` |
| `PyFrame_GetCode` | C-API | function | `frame_code` | Strong reference |
| `PyFrame_GetBack` | C-API | function | `frame_back` | NULL maps to `None` |
| `PyFrame_GetLocals` | C-API | function | `frame_locals` | Function frames may return PEP 667 `FrameLocalsProxy` |
| `PyFrame_GetGlobals` | C-API | function | `frame_globals` | Strong reference |
| `PyFrame_GetBuiltins` | C-API | function | `frame_builtins` | Strong reference |
| `PyFrame_GetGenerator` | C-API | function | `frame_generator` | NULL maps to `None` |
| `PyFrame_GetVar` | C-API | function | `frame_var` | Missing name raises `NameError`; cdef locals invisible |
| `PyFrame_GetVarString` | C-API | function | `frame_var_cstr` | Missing name raises `NameError` |
| `PyFrame_New` | C-API | function | `frame_new` | Cimport-only; unstable thread-state-dependent construction |
| `_PyFrame_IsEntryFrame` | C-API | unstable function | `frame_is_entry_frame` | Cimport-only implementation detail |
| `PyFrame_FastToLocals` / `PyFrame_FastToLocalsWithError` / `PyFrame_LocalsToFast` | C-API | deprecated functions | — | Soft-deprecated no-ops since 3.13; rejected |
| `PyUnstable_InterpreterFrame_*` | C-API | unstable functions | — | Requires internal header gated by `Py_BUILD_CORE`; rejected |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| `frame_check` | APPROVED | Tier A and Tier B measured wins; exact by non-subclassable frame type |
| `frame_lineno` | APPROVED | Tier A and Tier B measured wins |
| `frame_lasti` | APPROVED | Tier A wins; pass through CPython's scaled offset |
| `frame_code` | APPROVED | Tier A and Tier B measured wins |
| `frame_back` | APPROVED | Tier A and Tier B measured wins; NULL maps to None |
| `frame_locals` | APPROVED | Tier A win; preserve PEP 667 proxy |
| `frame_globals` | APPROVED | Tier A win |
| `frame_builtins` | APPROVED | Tier A win |
| `frame_generator` | APPROVED | Tier A win; NULL maps to None |
| `frame_var` | APPROVED | Tier A win; propagates NameError |
| `frame_var_cstr` | APPROVED | Tier A win; propagates NameError |
| `frame_new` | APPROVED (cimport) | Construction is unstable and thread-state-dependent; not a Python surface |
| `frame_is_entry_frame` | APPROVED (cimport) | Explicitly unstable implementation detail |
| `PyFrame_FastToLocals` / `PyFrame_FastToLocalsWithError` / `PyFrame_LocalsToFast` | REJECTED | Soft-deprecated no-ops since CPython 3.13 |
| `PyUnstable_InterpreterFrame_*` | REJECTED | Internal frame header requires `Py_BUILD_CORE`; not a public ABI |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 0 |
| Last pass | 2026-11-05 — full inventory, Tier A try-all + depth, Tier B checks |
| Next action | None; no subsequent queue order is inferred |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| `frame_check` | Direct type check beats `isinstance` | `bench/cyframe_bench.py`; Tier B harness | Tier A 0.63x / 0.40x; Tier B 0.37x / 0.35x | APPROVED | 0 |
| `frame_lineno` | C API line getter beats Python property | same | Tier A 0.69x / 0.73x; Tier B 0.64x / 0.70x | APPROVED | 0 |
| `frame_lasti` | C API offset getter beats property | Tier A harness | 0.50x / 0.45x | APPROVED | 0 |
| `frame_code` | C API code getter beats attribute | Tier A and Tier B harnesses | Tier A 0.50x / 0.49x; Tier B 0.26x / 0.24x | APPROVED | 0 |
| `frame_back` | C API back getter beats attribute | Tier A and Tier B harnesses | Tier A 0.44x / 0.66x; Tier B 0.34x / 0.34x | APPROVED | 0 |
| `frame_locals` | C API locals getter beats attribute | Tier A harness | 0.76x / 0.73x | APPROVED | 0 |
| `frame_globals` | C API globals getter beats attribute | Tier A harness | 0.51x / 0.54x | APPROVED | 0 |
| `frame_builtins` | C API builtins getter beats attribute | Tier A harness | 0.54x / 0.53x | APPROVED | 0 |
| `frame_generator` | C API generator getter beats Python path | Tier A harness | 0.67x / 0.67x | APPROVED | 0 |
| `frame_var` | C API name lookup beats locals mapping | Tier A harness | 0.28x / 0.28x | APPROVED | 0 |
| `frame_var_cstr` | C-string lookup beats locals mapping | Tier A harness | 0.59x / 0.61x | APPROVED | 0 |
| `frame_new` | Direct construction useful to Cython | ABI / safety review | Thread-state-dependent unstable API | APPROVED (cimport) | 0 |
| `frame_is_entry_frame` | Entry-frame detection useful to Cython | ABI review | Explicitly unstable API | APPROVED (cimport) | 0 |
| Deprecated sync helpers | Locals synchronization useful | CPython API review | No-op since 3.13 | REJECTED | 0 |
| Interpreter-frame APIs | Internal readers useful | Header / ABI review | Requires `Py_BUILD_CORE` internal header | REJECTED | 0 |

## Bench notes

- Harness: [`bench/cyframe_bench.py`](../../bench/cyframe_bench.py)
- Tier B harness: [`bench/tier_b/cyframe.py`](../../bench/tier_b/cyframe.py)
- Gate: [`docs/README.md`](../README.md) (mean ratio ≤ 0.95)
- Environment: CPython 3.15.0rc2, Linux x86_64, GIL build; Tier A default N=80,000 × RUNS=5; depth N=500,000 × RUNS=11; Tier B default N=2,000,000 and depth N=8,000,000, each 5 runs.

## Bench results

### Tier A (public helper vs plain Python)

Default pass, `CPY_BENCH_N=80,000`, `CPY_BENCH_RUNS=5`, `CPY_BENCH_WARMUP=0`:

|Label|picop ns/op|Python ns/op|Mean ratio|Runs|
|---|---:|---:|---:|---:|
|`frame_check`|37.75|59.63|0.63x|5|
|`frame_lineno`|62.38|90.63|0.69x|5|
|`frame_lasti`|28.13|56.63|0.50x|5|
|`frame_code`|30.50|61.25|0.50x|5|
|`frame_back`|33.00|74.13|0.44x|5|
|`frame_locals`|75.50|99.13|0.76x|5|
|`frame_globals`|31.00|60.38|0.51x|5|
|`frame_builtins`|30.75|57.50|0.54x|5|
|`frame_generator`|27.75|41.13|0.67x|5|
|`frame_var`|34.38|122.25|0.28x|5|
|`frame_var_cstr`|72.25|121.88|0.59x|5|

Depth pass, `CPY_BENCH_N=500000`, `CPY_BENCH_RUNS=11`:

|Label|picop ns/op|Python ns/op|Mean ratio|Runs|
|---|---:|---:|---:|---:|
|`frame_check`|28.82|72.18|0.40x|11|
|`frame_lineno`|66.04|90.96|0.73x|11|
|`frame_lasti`|30.42|67.42|0.45x|11|
|`frame_code`|33.46|68.96|0.49x|11|
|`frame_back`|38.16|57.48|0.66x|11|
|`frame_locals`|76.96|105.80|0.73x|11|
|`frame_globals`|30.88|57.28|0.54x|11|
|`frame_builtins`|32.48|60.72|0.53x|11|
|`frame_generator`|27.82|41.32|0.67x|11|
|`frame_var`|34.88|125.10|0.28x|11|
|`frame_var_cstr`|75.18|123.60|0.61x|11|

### Tier B (cdef loop vs typed Cython baseline)

Default pass, `CPY_TIERB_N=2,000,000` (5 runs):

|Label|Baseline ns/op|picop ns/op|Ratio|
|---|---:|---:|---:|
|`frame_check`|3.725|1.365|0.37x|
|`frame_lineno`|39.785|25.390|0.64x|
|`frame_code`|17.730|4.635|0.26x|
|`frame_back`|14.260|4.810|0.34x|

Depth pass, `CPY_TIERB_N=8,000,000` (5 runs):

|Label|Baseline ns/op|picop ns/op|Ratio|
|---|---:|---:|---:|
|`frame_check`|4.253|1.496|0.35x|
|`frame_lineno`|39.073|27.391|0.70x|
|`frame_code`|19.293|4.663|0.24x|
|`frame_back`|14.539|4.958|0.34x|

Every Tier A helper passed the ≤0.95 mean gate in both passes; no public helper was demoted.

## Experiment conclusions

- **Why and scale.** All eleven public helpers beat their plain-Python baselines in both the default and depth runs; the per-operation ratios are recorded above verbatim. The four Tier B cases also beat the typed Cython attribute baseline in both runs, from 0.24x through 0.70x. The stable pattern across N=80,000/500,000 and Tier B N=2,000,000/8,000,000 supports retaining the complete measured public surface, not just the four Tier B cases.
- **Ownership and safety.** Frame getters return new references. `GetBack` and `GetGenerator` can produce NULL and wrappers return `None`; `GetVar` and `GetVarString` raise `NameError` for absent variables and the wrappers propagate it. Keep the frame alive across calls to `frame_back`, `frame_generator`, and `frame_var` under free-threading because those getters are not internally lock-protected; Cython `cdef` locals are invisible to `PyFrame_GetVar`.
- **Semantic boundary.** `frame_locals` preserves the PEP 667 `FrameLocalsProxy` on function frames rather than copying to a dict. `PyFrame_Check` is already exact because frames are unsubclassable. `GetLasti` is passed through unchanged because CPython already scales the instruction offset. CPython internally locks GetCode, GetLocals, GetLasti, and GetLineNumber, but not GetBack, GetGenerator, or GetVar.
- **Rejected and cimport-only ABI.** The locals synchronization APIs are soft-deprecated no-ops since 3.13; interpreter-frame readers require private headers and `Py_BUILD_CORE`, so neither is a supported ABI surface. Frame construction remains cimport-only because `PyFrame_New` depends on thread state and is unstable; `_PyFrame_IsEntryFrame` is explicitly an implementation detail. These constraints are safety and ABI decisions, not benchmark omissions.

## Done when

- [x] Full inventory vs mapped include (or declared custom surface)
- [x] Every row has workflow status
- [x] Lifecycle + next action filled
- [x] APPROVED / APPROVED (cimport) rows have decision-log evidence
- [x] REJECTED rows have policy or measured why
- [x] Present measuring: try-all **and** depth checklist in this tracker's Experiment conclusions
- [x] Bench results table filled in this file
- [x] Public PEP 257 one-liners in `cyframe.pyi`; `.pxd` lean — [`PIPELINE.md`](../PIPELINE.md)
