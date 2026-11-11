# cysys

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython/sysmodule.h` |
| Sources | `src/picop/cysys.*`, `src/picop/cysys_shim.h` |
| Surface | public + cimport |
| Tracker lifecycle | decided (Tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

The public surface keeps the one required sys attribute getter that wins Tier A and preserves CPython's missing-attribute exception contract. Borrowed getters and helpers with Python-boundary losses remain cimport-only. CPython 3.15-only declarations are protected by the compile-time API-version guard, so 3.14 builds use explicit NotImplementedError shims without referencing unavailable ABI symbols.

## Inventory

Full callable surface of `sysmodule.h` across CPython 3.14 and 3.15.

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| `PySys_GetObject` | C-API | function | `sys_get_object` (cimport) | Borrowed result; owned return; NULL miss without exception |
| `PySys_SetObject` | C-API | function | `sys_set_object_cstr` (cimport) | NULL deletes; 0/-1 |
| `PySys_GetAttr` | C-API (3.15) | function | `sys_get_attr` | New reference; RuntimeError on miss |
| `PySys_GetAttrString` | C-API (3.15) | function | `sys_get_attr_string` (cimport) | New reference; RuntimeError on miss |
| `PySys_GetOptionalAttr` | C-API (3.15) | function | `sys_get_optional_attr` (cimport) | 1 new ref, 0 absent/NULL, -1 error |
| `PySys_GetOptionalAttrString` | C-API (3.15) | function | `sys_get_optional_attr_string` (cimport) | 1 new ref, 0 absent/NULL, -1 error |
| `PySys_WriteStdout` | C-API | function | `sys_write_stdout_cstr` (cimport) | Fixed `%s` format, 1000-byte truncation, never raises |
| `PySys_WriteStderr` | C-API | function | `sys_write_stderr_cstr` (cimport) | Fixed `%s` format, 1000-byte truncation, never raises |
| `PySys_FormatStdout` | C-API | function | `sys_format_stdout_cstr` (cimport) | Fixed `%s` format; Unicode formatter, no 1000-byte truncation |
| `PySys_FormatStderr` | C-API | function | `sys_format_stderr_cstr` (cimport) | Fixed `%s` format; Unicode formatter, no 1000-byte truncation |
| `PySys_GetXOptions` | C-API | function | `sys_get_xoptions` (cimport) | Borrowed result; owned return |
| `PySys_SetArgv` | C-API | candidate | — | REJECTED: deprecated since 3.11; process-global startup mutation |
| `PySys_SetArgvEx` | C-API | candidate | — | REJECTED: deprecated since 3.11; process-global startup mutation |
| `PySys_ResetWarnOptions` | C-API (3.14) | candidate | — | REJECTED: deprecated and removed in 3.15 |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| `sys_get_object` | APPROVED (cimport) | Tier A 1.07x from the Python boundary; borrowed-result/no-exception semantics remain useful to typed callers |
| `sys_set_object_cstr` | APPROVED (cimport) | Public candidate 1.23x versus setattr rejected; Cython callers retain NULL deletion |
| `sys_get_attr` | APPROVED | Tier A 0.42x; preserves RuntimeError on absent required attributes |
| `sys_get_attr_string` | APPROVED (cimport) | Public candidate 1.08x versus getattr rejected; direct Cython call remains available |
| `sys_get_optional_attr` | APPROVED (cimport) | Preserves the 1/0/-1 status and new-reference result contract |
| `sys_get_optional_attr_string` | APPROVED (cimport) | Preserves the 1/0/-1 status and new-reference result contract |
| `sys_write_stdout_cstr` | APPROVED (cimport) | Public candidate 1.20x rejected; Cython callers keep CPython's bounded output API |
| `sys_write_stderr_cstr` | APPROVED (cimport) | Public candidate 1.21x rejected; Cython callers keep CPython's bounded output API |
| `sys_format_stdout_cstr` | APPROVED (cimport) | Public candidate 1.15x rejected; Cython callers keep Unicode formatting |
| `sys_format_stderr_cstr` | APPROVED (cimport) | Public candidate 1.24x rejected; Cython callers keep Unicode formatting |
| `sys_get_xoptions` | APPROVED (cimport) | Public candidate 1.49x versus `sys._xoptions` rejected; typed call is separately measured in Tier B |
| `PySys_SetArgv` | REJECTED | Deprecated startup mutation |
| `PySys_SetArgvEx` | REJECTED | Deprecated startup mutation |
| `PySys_ResetWarnOptions` | REJECTED | Removed in CPython 3.15 |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 2 |
| Last pass | 2026-11-11 — full header inventory, ownership tests, Tier A/B measurement, API demotions |
| Next action | None |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| `PySys_GetObject` | Direct C lookup could reduce Python attribute cost | Tier A candidate | 1.07x; baseline faster | Public form REJECTED; cimport kept | 2 |
| `PySys_SetObject` | NULL value deletes the sys attribute | Tier A candidate | 1.23x; `setattr` faster | Public form REJECTED; cimport kept | 2 |
| `PySys_GetAttr` | Required 3.15 getter has useful failure semantics and speed | Tier A | 0.42x versus `getattr` | APPROVED | 2 |
| `PySys_GetAttrString` | String getter could avoid attribute lookup overhead | Tier A candidate | 1.08x versus `getattr` | Public form REJECTED; cimport kept | 2 |
| `PySys_GetOptionalAttr` | Optional lookup avoids exception for absence | API contract + Cython smoke | 1/0/-1 results; new reference on hit | APPROVED (cimport) | 2 |
| `PySys_GetOptionalAttrString` | Optional string lookup avoids exception for absence | API contract + Cython smoke | 1/0/-1 results; NULL on miss | APPROVED (cimport) | 2 |
| `PySys_WriteStdout` | CPython writer retains its own stream/truncation semantics | Tier A candidate | 1.20x; slower; 1000-byte cap | Public form REJECTED; cimport kept | 2 |
| `PySys_WriteStderr` | CPython writer retains its own stream/truncation semantics | Tier A candidate | 1.21x; slower; 1000-byte cap | Public form REJECTED; cimport kept | 2 |
| `PySys_FormatStdout` | Unicode formatter avoids Write* truncation | Tier A candidate | 1.15x; slower than `sys.stdout.write` | Public form REJECTED; cimport kept | 2 |
| `PySys_FormatStderr` | Unicode formatter avoids Write* truncation | Tier A candidate | 1.24x; slower than `sys.stderr.write` | Public form REJECTED; cimport kept | 2 |
| `PySys_GetXOptions` | C getter avoids Python attribute lookup | Tier A candidate | 1.49x; `sys._xoptions` faster | Public form REJECTED; cimport kept | 2 |
| `PySys_SetArgv` | Legacy argv API may support embedding | Header lifecycle | Deprecated since 3.11 | REJECTED | 2 |
| `PySys_SetArgvEx` | Legacy argv API may support embedding | Header lifecycle | Deprecated since 3.11 | REJECTED | 2 |
| `PySys_ResetWarnOptions` | Warning option reset may be useful | Header lifecycle | Deprecated in 3.14, absent in 3.15 | REJECTED | 2 |

## Bench notes

- Harness: `bench/cysys_bench.py` and `bench/tier_b/cysys.py` / `cysys_tb.pyx`
- Tier A gate: mean ratio ≤ 0.95, or ≤ 1.02 with an API-clarity keep note.
- Environment: CPython 3.15.0rc2 Linux x86_64 GIL; Tier A N=80,000 ×5; Tier B N=2,000,000 ×5.
- The initial public-candidate comparisons for `sys_set_object` and four output functions ran on CPython 3.14.7 Linux x86_64 GIL at Tier A N=80,000 ×5; the getter candidate comparisons and accepted `sys_get_attr` run used CPython 3.15.0rc2.

## Bench results

### Tier A

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| `sys_get_attr` | `sys.version` | 2.95±0.06 ms | 3.03 ms | 0.42x | 0.37x | picop faster |
| `sys_get_object` (candidate) | `sys.version` | 6.98±0.08 ms | 7.09 ms | 1.07x | 1.07x | public candidate rejected |
| `sys_get_xoptions` (candidate) | `sys._xoptions` | 5.69±2.62 ms | 8.71 ms | 1.49x | 2.24x | public candidate rejected |
| `sys_get_attr_string` (candidate) | `sys.version` | 7.10±0.08 ms | 7.18 ms | 1.08x | 1.08x | public candidate rejected |
| `sys_set_object` (candidate) | `setattr(sys, name, value)` | 16.87±4.59 ms | 22.57 ms | 1.23x | 1.57x | public candidate rejected |
| `sys_write_stdout` (candidate) | output | 179.29±10.91 ms | 194.07 ms | 1.20x | 1.23x | public candidate rejected |
| `sys_write_stderr` (candidate) | output | 173.87±8.35 ms | 183.82 ms | 1.21x | 1.10x | public candidate rejected |
| `sys_format_stdout` (candidate) | output | 169.27±7.11 ms | 180.13 ms | 1.15x | 1.16x | public candidate rejected |
| `sys_format_stderr` (candidate) | output | 184.78±5.40 ms | 189.37 ms | 1.24x | 1.20x | public candidate rejected |

### Tier B

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | verdict |
|-----------|------|-------------|-----|----------------|-------|------|---------|
| `sys_get_object` | version, N=2,000,000 | 136.37±2.42 ms | 139.60 ms | 43.27±1.36 ms | 3.15x | 3.12x | baseline faster |
| `sys_get_xoptions` | `_xoptions`, N=2,000,000 | 32.70±1.30 ms | 34.85 ms | 44.41±6.08 ms | 0.74x | 0.64x | picop faster |
| `sys_get_attr` | version, N=2,000,000 | 24.35±0.23 ms | 24.60 ms | 40.22±0.29 ms | 0.61x | 0.60x | picop faster |
| `sys_get_attr_string` | version, N=2,000,000 | 116.64±0.34 ms | 117.06 ms | 40.86±1.70 ms | 2.85x | 2.68x | baseline faster |

## Experiment conclusions

Tier A keeps only `sys_get_attr` as a Python-visible operation after comparative probes of every candidate: it is 0.47x versus `getattr`. `sys_get_object` (1.07x), `sys_get_xoptions` (1.49x), `sys_get_attr_string` (1.08x), the setter (1.23x), and the four stream wrappers (1.15–1.24x) exceed the 1.02x ceiling and were demoted from Python exports/stubs/benchmark labels; their Cython-only forms remain available where their C-API semantics are needed. In Tier B, `sys_get_xoptions` and `sys_get_attr` are faster (0.78x, 0.55x), while the two string/C-string loops are slower. `PySys_GetObject` and `PySys_GetXOptions` return borrowed pointers; the cimport wrappers promote those pointers to owned references, so callers may safely retain them after the source mapping changes. `PySys_GetAttr*` return new references and required misses preserve RuntimeError; optional helpers preserve the 1/new-ref, 0/NULL/no-exception, and -1/error contract. This avoids translating a normal optional miss into SystemError. The shim's `PY_VERSION_HEX` guard prevents unresolved 3.15 ABI references in 3.14 builds; 3.14 fallback calls raise NotImplementedError. Writer calls use a constant `%s` format, so input percent sequences remain literal; a NUL byte terminates the C string and trailing bytes are not written. Write* truncates after 1000 bytes. Deprecated argv mutation and removed ResetWarnOptions remain rejected.

## Done when

- [x] Full inventory and candidate decisions recorded
- [x] Every inventory symbol has a workflow decision
- [x] Borrowed and new-reference ownership contracts tested
- [x] Tier A/Tier B results and depth conclusions recorded
- [x] Public stub summaries and lean Cython declarations
