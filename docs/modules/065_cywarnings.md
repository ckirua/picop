# cywarnings

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `Python.h` warning / import APIs |
| Sources | `src/picop/cywarnings.*` |
| Surface | public + cimport |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

Issue CPython warnings through its active filter from typed Cython code and retrieve the warnings module. Preserve filter behavior and exception propagation rather than reimplementing policy in Python.

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| `PyErr_WarnEx` | C-API | function | `warn_ex` | Public; emits using warning machinery |
| `PyErr_WarnExplicitObject` | C-API | function | `warn_explicit` | Explicit filename, line, module and registry |
| `PyModule_GetWarningsModule` | C-API | function | `warnings_module` | Current supported headers do not declare/export it; helper uses `PyImport_AddModuleRef("warnings")` |
| `PyErr_Warn` | deprecated alias | function | — | Deprecated equivalent of WarnEx |
| `PyErr_WarnExplicitFormat` | C-API | variadic function | — | Variadic format args are not safely representable in Cython's typed wrapper |
| `PyImport_AddModuleRef` | C-API | function | internal helper | Returns warnings module without running a Python import |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| `warn_ex` | APPROVED | Thin C-API wrapper; preserves CPython warning filtering |
| `warn_explicit` | APPROVED | Thin object-argument wrapper; explicit source-location semantics |
| `warnings_module` | APPROVED | Header/symbol unavailable in installed CPython 3.14/3.15; same module-dict behavior via `PyImport_AddModuleRef` |
| `PyErr_Warn` | REJECTED | Deprecated alias; `PyErr_WarnEx` takes explicit stacklevel and is the supported API |
| `PyErr_WarnExplicitFormat` | REJECTED | Variadic formatting cannot be safely bound as a normal Cython helper; use object variant |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 0 |
| Last pass | 2026-11-10 — warning edge probes, Tier A/B timings, barrel smoke, and all gates passed |
| Next action | None; no subsequent queue order is inferred |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| `PyErr_WarnEx` | Direct C-API call avoids Python call dispatch | Tier A/B | Tier A mean ratio 0.94x overall; ordinary warn case 1.04x, stacklevel=2 case 0.85x | APPROVED | 0 |
| `PyErr_WarnExplicitObject` | Explicit route enables Cython source warnings | probe | explicit filename/line and both `None` and dict registries work | APPROVED | 0 |
| `PyModule_GetWarningsModule` | Cached module retrieval avoids lookup | header probe | no declaration/symbol in installed CPython 3.14/3.15; implemented equivalent via `PyImport_AddModuleRef` | APPROVED | 0 |
| `PyErr_Warn` | Deprecated alias offers no useful distinct semantics | — | Superseded by WarnEx with explicit stacklevel | REJECTED | 0 |
| `PyErr_WarnExplicitFormat` | C variadic format wrapper useful to Python API | — | Variadic call cannot be safely represented | REJECTED | 0 |

## Bench notes

- Harness: [`bench/cywarnings_bench.py`](../../bench/cywarnings_bench.py); Tier B [`bench/tier_b/cywarnings.py`](../../bench/tier_b/cywarnings.py)
- Gate: [`docs/README.md`](../README.md) (mean ratio ≤ 0.95)
- Env: CPython 3.14.7, Linux x86_64, GIL build; Tier A N=80,000 × RUNS=5; Tier B N=2,000,000 × RUNS=5.

## Bench results

### Tier A

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| `warn_ex` | ignored warning vs `warnings.warn` | 35.32±0.34ms | 35.71ms | 1.04x | 1.03x | baseline +4% |
| `warn_ex` | ignored warning vs `warnings.warn(stacklevel=2)` | 35.15±0.29ms | 35.40ms | 0.85x | 0.83x | picop +15% (gate) |

### Tier B

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| `warn_ex` | ignored warning, typed Cython loop N=2,000,000 | 805.01±6.33ms | 812.72ms | 787.22±22.93ms | **1.02x** | 0.98x | baseline faster by 2%; API-clarity keep |

## Experiment conclusions

`PyErr_WarnEx` enters CPython's warning machinery, which evaluates filters and records suppression state in a per-module registry; ignored warnings still pay category/message and filter matching costs, so the C call's savings are limited to Python-level dispatch. Tier A's plain `warnings.warn` case is a measured 1.04x loss, while specifying `stacklevel=2` makes `warn_ex` 0.85x the Python baseline because Python's helper must walk an additional frame; the two-case mean is 0.94x. Tier B's Cython-loop comparison is a 1.02x loss, effectively the cost of warning-object/category validation and Cython wrapper dispatch around an operation whose filter machinery dominates. CPython returns C integer zero for emitted and ignored warnings and -1 with the selected warning exception set when the filter is `error`; Cython's `except -1` propagates that exception. Tests confirm the success result is Python `False`, and the error path raises `RuntimeWarning` instead of returning. Stacklevel 1 reports the caller's line; 2 reports the caller above a helper, as expected. `PyErr_WarnExplicitObject` with registry `None` and with a dictionary both emits at the given filename/line; if module is omitted, this wrapper supplies filename because a null module silently suppressed emission in the direct probe. The C API accepted `str` as category and emitted a malformed warning rather than raising; wrapper validation therefore rejects non-`Warning` classes with `TypeError`. These APIs require the GIL because filter and registry handling touches Python state. `PyModule_GetWarningsModule` is absent from installed CPython 3.14/3.15 headers, so the exposed accessor currently uses `PyImport_AddModuleRef(\"warnings\")` rather than linking a nonexistent symbol.
Scale and ABI evidence: the warning tests exercise stacklevel 1 and 2 (the latter crosses a Cython helper frame), while Tier A fixes N=80,000 for both plain and stacklevel baselines; the Tier B typed loop runs N=2,000,000. Header inspection on CPython 3.14 and 3.15 confirmed no `PyModule_GetWarningsModule` declaration or linkable symbol, so the replacement relies on the public `PyImport_AddModuleRef` ABI.

Internal notes: `PyImport_AddModuleRef("warnings")` returns a new reference; `warnings_module()` transfers that reference as its Python object result without an extra incref. CPython imports `warnings` during startup, so a null result is an exotic embedding case; the inline helper returns `None` without attempting to import or dereference it.

## Done when

- [x] Full custom API inventory and decisions
- [x] Public one-line `.pyi` docs
- [x] Timed Tier A/B tables and all required gates passed
