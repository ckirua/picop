# cycode

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.code` |
| Sources | `src/picop/cycode.*` |
| Surface | public + cimport |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

Expose thin CPython code-object readers for Cython callers and runtime inspection. The module uses stable code APIs for bytecode-derived tuples and address-to-line mapping, and a narrow shim for fields not exposed through public getter functions. Code objects are effectively immutable, but their bytecode representation is adaptive and version-specific; this surface deliberately does not promise structural equality.

## Inventory

Full selected code-object accessor surface. Raw fields are accessed through the shim; unsupported construction, callbacks, and unstable extras are recorded as rejected.

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| `PyCode_Check` | C-API | macro | `code_check` | Exact code-object check |
| `co_name` | C-API | shim accessor | `code_name` | `Py_NewRef` |
| `co_qualname` | C-API | shim accessor | `code_qualname` | `Py_NewRef` |
| `co_filename` | C-API | shim accessor | `code_filename` | `Py_NewRef` |
| `co_firstlineno` | C-API | shim accessor | `code_firstlineno` | Scalar returned by value |
| `co_argcount` | C-API | shim accessor | `code_argcount` | Scalar returned by value |
| `co_posonlyargcount` | C-API | shim accessor | `code_posonlyargcount` | Scalar returned by value |
| `co_kwonlyargcount` | C-API | shim accessor | `code_kwonlyargcount` | Scalar returned by value |
| `co_consts` | C-API | shim accessor | `code_consts` | `Py_NewRef` |
| `co_names` | C-API | shim accessor | `code_names` | `Py_NewRef` |
| `PyCode_GetCode` | C-API | function | `code_code` | Bytes reflect adaptive, version-dependent bytecode |
| `PyCode_GetVarnames` | C-API | function | `code_varnames` | Strong reference |
| `PyCode_GetCellvars` | C-API | function | `code_cellvars` | Strong reference |
| `PyCode_GetFreevars` | C-API | function | `code_freevars` | Strong reference |
| `PyCode_Addr2Line` | C-API | function | `code_addr2line` | Maps instruction address to source line |
| `PyCode_GetNumFree` | C-API | function | `code_num_free` | Cimport-only scalar reader |
| `PyCode_Addr2Location` | C-API | function | `code_addr2_location` | Cimport-only location tuple |
| `PyCode_New` / `PyUnstable_Code_New` | C-API | function | — | Construction API; unsupported construction/unstable ABI |
| `PyUnstable_Code_GetExtra` | C-API | function | — | Unstable ABI |
| `PyUnstable_Code_SetExtra` | C-API | function | — | Unstable ABI |
| `PyCode_AddWatcher` | C-API | function | — | C callback ABI |
| `PyCode_ClearWatcher` | C-API | function | — | C callback ABI |
| `PyCode_Optimize` | C-API | deprecated function | — | Legacy peephole path |
| `code_eq` | cypy | candidate | — | Structural comparison is expensive and version-sensitive; use identity via `obj_eq` |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| `code_check` | APPROVED | Tier A and Tier B wins |
| `code_name` | APPROVED | Tier A and Tier B wins |
| `code_qualname` | APPROVED | Tier A wins |
| `code_filename` | APPROVED | Tier A wins |
| `code_firstlineno` | APPROVED | Tier A and Tier B wins |
| `code_argcount` | APPROVED | Tier A and Tier B wins |
| `code_posonlyargcount` | APPROVED | Tier A wins |
| `code_kwonlyargcount` | APPROVED | Tier A wins |
| `code_consts` | APPROVED | Tier A wins |
| `code_names` | APPROVED | Tier A wins |
| `code_code` | APPROVED | Tier A wins |
| `code_varnames` | APPROVED | Tier A wins |
| `code_cellvars` | APPROVED | Tier A wins |
| `code_freevars` | APPROVED | Tier A wins |
| `code_addr2line` | APPROVED | Tier A wins; baseline caveat recorded |
| `code_num_free` | APPROVED (cimport) | Cython-only scalar reader |
| `code_addr2_location` | APPROVED (cimport) | Cython-only detailed location reader |
| `PyCode_New` / `PyUnstable_Code_New` | REJECTED | Construction and unstable ABI are outside the reader surface |
| `PyUnstable_Code_GetExtra` / `PyUnstable_Code_SetExtra` | REJECTED | Unstable ABI |
| `PyCode_AddWatcher` / `PyCode_ClearWatcher` | REJECTED | C callback ABI is not a Python helper surface |
| `PyCode_Optimize` | REJECTED | Legacy peephole path |
| `code_eq` | REJECTED | Expensive, version-sensitive structure; identity uses `obj_eq` (`docs/EQ_RUNTIME.md:43`) |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 0 |
| Last pass | 2026-11-05 — full inventory, Tier A try-all + depth, Tier B checks |
| Next action | None; no subsequent queue order is inferred |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| Public helpers (15) | Thin wrappers beat attribute baselines | Tier A harness | All ratios ≤0.65x across default and depth | APPROVED | 0 |
| `code_check` / `code_name` / `code_firstlineno` / `code_argcount` | Direct C access beats typed attribute baseline | Tier B harness | 0.15–0.37x in both passes | APPROVED | 0 |
| `code_num_free` / `code_addr2_location` | Useful low-level Cython readers | API review | C-only surface | APPROVED (cimport) | 0 |
| shim object readers (`code_name`/`code_qualname`/`code_filename`/`code_consts`/`code_names`) | `<object>PyObject *` cast of a `Py_NewRef` result is safe | `sys.getrefcount` drift probe, 2 000 calls | leaked one reference per call (+2000 refs); `object`-declared externs measure 0 | APPROVED (fix) | 1 |
| Construction / extras / watchers / optimizer | Candidate APIs add value | ABI and lifecycle review | Construction or unstable ABI; callback ABI; legacy path | REJECTED | 0 |
| `code_eq` | Structural equality could aid callers | Policy review | Expensive, adaptive/version-sensitive structure; identity already supported | REJECTED | 0 |

## Bench notes

- Harness: [`bench/cycode_bench.py`](../../bench/cycode_bench.py)
- Tier B harness: [`bench/tier_b/cycode.py`](../../bench/tier_b/cycode.py)
- Gate: [`docs/README.md`](../README.md) (mean ratio ≤ 0.95)
- Environment: CPython 3.15.0rc2, Linux x86_64, GIL build; Tier A default N=80,000 × RUNS=5; depth N=500,000 × RUNS=11; Tier B default N=2,000,000 and depth N=8,000,000, each 5 runs.

## Bench results

### Tier A (public helper vs plain Python)

Default pass, `CPY_BENCH_N=80,000`, `CPY_BENCH_RUNS=5`:

|Label|picop ns/op|Python ns/op|Mean ratio|Runs|
|---|---:|---:|---:|---:|
|`code_check`|26.75|60.25|0.44x|5|
|`code_name`|26.13|65.38|0.40x|5|
|`code_qualname`|27.13|43.38|0.63x|5|
|`code_filename`|26.75|46.13|0.58x|5|
|`code_firstlineno`|27.25|58.00|0.47x|5|
|`code_argcount`|28.50|60.75|0.47x|5|
|`code_posonlyargcount`|26.38|61.00|0.43x|5|
|`code_kwonlyargcount`|25.88|61.25|0.42x|5|
|`code_consts`|27.50|44.63|0.62x|5|
|`code_names`|27.75|42.13|0.66x|5|
|`code_code`|31.00|57.13|0.54x|5|
|`code_varnames`|33.38|58.88|0.57x|5|
|`code_cellvars`|30.25|58.75|0.52x|5|
|`code_freevars`|31.13|59.38|0.52x|5|
|`code_addr2line` (addr=0, `co_firstlineno` baseline)|36.63|64.50|0.57x|5|

Depth pass, `CPY_BENCH_N=500000`, `CPY_BENCH_RUNS=11`:

|Label|picop ns/op|Python ns/op|Mean ratio|Runs|
|---|---:|---:|---:|---:|
|`code_check`|26.26|58.28|0.45x|11|
|`code_name`|25.88|43.32|0.60x|11|
|`code_qualname`|27.92|43.30|0.64x|11|
|`code_filename`|26.76|51.54|0.52x|11|
|`code_firstlineno`|27.92|59.10|0.47x|11|
|`code_argcount`|26.44|58.80|0.45x|11|
|`code_posonlyargcount`|26.48|59.42|0.45x|11|
|`code_kwonlyargcount`|26.18|63.82|0.41x|11|
|`code_consts`|28.50|44.10|0.65x|11|
|`code_names`|25.60|42.74|0.60x|11|
|`code_code`|31.54|57.56|0.55x|11|
|`code_varnames`|31.08|56.20|0.55x|11|
|`code_cellvars`|31.24|68.82|0.45x|11|
|`code_freevars`|31.28|57.60|0.54x|11|
|`code_addr2line` (addr=0, `co_firstlineno` baseline)|38.10|63.44|0.60x|11|

### Tier B (cdef loop vs typed Cython baseline)

Default pass, `CPY_TIERB_N=2,000,000` (5 runs):

|Label|Baseline ns/op|picop ns/op|Ratio|
|---|---:|---:|---:|
|`code_check`|3.68|1.37|0.37x|
|`code_name`|14.39|2.49|0.17x|
|`code_firstlineno`|16.28|2.53|0.16x|
|`code_argcount`|17.44|2.70|0.15x|

Depth pass, `CPY_TIERB_N=8,000,000` (5 runs):

|Label|Baseline ns/op|picop ns/op|Ratio|
|---|---:|---:|---:|
|`code_check`|4.01|1.48|0.37x|
|`code_name`|14.89|2.59|0.17x|
|`code_firstlineno`|17.58|2.54|0.14x|
|`code_argcount`|18.23|2.66|0.15x|

## Experiment conclusions

- **Why and scale.** All fifteen public helpers pass the ≤0.95 mean gate in both Tier A runs. The stable outcomes at N=80,000 and N=500,000 support retaining the complete API, while all four Tier B cases also win across N=2,000,000 and N=8,000,000. `code_addr2line` has a specific baseline caveat: address zero is compared with `co_firstlineno`, the cheapest attribute read, so this is a lower bound rather than a like-for-like disassembly lookup.
- **Semantics and reference ownership.** The shim returns new references with `Py_NewRef` for object fields and returns scalar fields by value, avoiding borrowed-reference lifetime hazards. Code objects are effectively immutable, but `co_code` can reflect adaptive bytecode and must not be treated as a cross-version structural identity. `PyFrame_GetLasti` consumers should preserve CPython's bytecode-unit offset convention; `co_firstlineno` and `code_addr2line` provide distinct line metadata, and address-to-line mapping remains an instruction-address operation.
- **Safety and rejected surfaces.** Free-threading safety relies on owning getter results and immutable code-object state; no extra nested critical section is introduced around shim reads. Construction, unstable extra-data APIs, callback-based watchers, and the legacy peephole optimizer have incompatible ABI/lifecycle or maintenance characteristics. `code_eq` remains rejected because adaptive code and version-dependent structure make comparisons expensive and unstable; object identity through `obj_eq` is the supported pattern (see `docs/EQ_RUNTIME.md:43`).

## Done when

- [x] Full inventory vs mapped include (or declared custom surface)
- [x] Every row has workflow status
- [x] Lifecycle + next action filled
- [x] APPROVED / APPROVED (cimport) rows have decision-log evidence
- [x] REJECTED rows have policy or measured why
- [x] Present measuring: try-all **and** depth checklist in this tracker's Experiment conclusions
- [x] Bench results table filled in this file
- [x] Public PEP 257 one-liners in `cycode.pyi`; `.pxd` lean — [`PIPELINE.md`](../PIPELINE.md)
