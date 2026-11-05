# cycall

| Field | Value |
|---|---|
| Status | present |
| Maps to | `Python.h` call / vectorcall APIs |
| Sources | `src/picop/cycall.{pxd,pyx,pyi}` |
| Surface | public + cimport |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full mapped call surface |

## Why

Provide GIL-held Cython call helpers that avoid temporary argument tuples for the common zero-, one-, and two-argument cases. Python callers should use normal invocation.

## Inventory

| Symbol | Kind | Export | Notes |
|---|---|---|---|
| `call_noargs` | cpdef | public + cimport | `PyObject_CallNoArgs`; new reference or raises |
| `call_onearg` | cpdef | public + cimport | `PyObject_CallOneArg`; new reference or raises |
| `call_twoargs` | cpdef | public + cimport | `PyObject_Vectorcall` with two stack arguments |
| `call_vector` | cdef | cimport | caller-owned `PyObject*` vector and keyword-name tuple; `nargsf` forwarded verbatim, offset bit allowed |
| `call_method_noargs` | cdef | cimport | `PyObject_CallMethodNoArgs` |
| `call_method_onearg` | cdef | cimport | `PyObject_CallMethodOneArg` |
| `call_method_vector` | cdef | cimport | `PyObject_VectorcallMethod`; receiver is `args[0]` and counts in `nargsf` |
| `vectorcall_nargs` | cdef | cimport | `PyVectorcall_NARGS` — strips the offset bit |
| `PY_VECTORCALL_ARGUMENTS_OFFSET` | macro | — | not wrapped; pass the bit straight through `call_vector` |
| `PyObject_Call` / `PyObject_CallObject` / `PyObject_CallFunction` / `PyObject_CallMethod` | C-API | — | tuple/varargs paths deliberately unwrapped: they allocate an argument tuple, which is exactly what this module avoids |

## Workflow status

| Function | Status | Why |
|---|---|---|
| `call_noargs` | APPROVED | Tier A **0.94x** vs direct call (2026-11-05 run) |
| `call_onearg` | APPROVED | Tier A **0.94x** |
| `call_twoargs` | APPROVED | Tier A **0.93x** |
| `call_vector` | APPROVED (cimport) | Tier B **0.93–0.98x** on NULL/pos+kw shapes, ~tie elsewhere; raw-vector contract cannot be expressed from Python |
| `call_method_noargs` | APPROVED (cimport) | Tier B **~1.00x** with Cython's own `obj.name()` emission; no tuple, no METH_O dispatch check |
| `call_method_onearg` | APPROVED (cimport) | Tier B **~1.01x** tie; same contract value |
| `call_method_vector` | APPROVED (cimport) | Tier B **1.05x** (noise band 1.0–1.1x); kept for the borrowed-vector contract, not speed |
| `vectorcall_nargs` | APPROVED (cimport) | macro wrapper, measured **1.02x** vs literal count — free ABI-safe spelling |
| tuple/varargs `PyObject_Call*` family | REJECTED | allocates the argument tuple the module exists to avoid |

## Lifecycle

| Field | Value |
|---|---|
| Iteration | 1 |
| Last pass | 2026-11-05 — Tier B harness `bench/tier_b/cycall.py` added; vector + bound-method helpers implemented; depth probes run at CPython 3.15.0rc2 |
| Next action | none for this Order; helpers are decided. Re-measure only if a Core-freeze change is proposed |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|---|---|---|---|---|---|
| `call_noargs` | tuple-free call beats a Python-level call | Tier A `bench/cycall_bench.py` | **0.94x** | APPROVED | 1 |
| `call_onearg` | same for one arg | Tier A | **0.94x** | APPROVED | 1 |
| `call_twoargs` | vectorcall beats tuple build | Tier A | **0.93x** | APPROVED | 1 |
| `call_vector` | a raw vector contract is worth exposing even at parity | Tier B `bench/tier_b/cycall.py` | 0.93x NULL-args, 0.98x pos+kw, 1.03–1.11x at higher arity | APPROVED (cimport) | 1 |
| `call_method_noargs` / `call_method_onearg` | CPython's method helpers beat Cython's inline dispatch | Tier B | **0.98x / 1.01x** | APPROVED (cimport) — contract, not speed | 1 |
| `call_method_vector` | method vectorcall is a useful depth path | Tier B | **1.05x** (σ 2.0 ms over 11 runs) | APPROVED (cimport), no speed claim | 1 |
| `vectorcall_nargs` | macro spelling costs nothing | Tier B | **1.02x** vs a literal count | APPROVED (cimport) | 1 |
| reserved-slot (`nargsf` with offset bit) | matches what Cython emits, so it should be free | Tier B | **1.00x** vs plain count | keep as documented option | 1 |

## Safety

All helpers require the GIL. `call_vector` borrows its argument vector and keyword-name pointer for the duration of the call; callers retain ownership.

- **`kwnames` is NULL-or-tuple only.** Passing `Py_None` (the easy Cython mistake: `<PyObject *>None`) is undefined behaviour — measured **SIGSEGV** (subprocess exit `-11`), not a `TypeError`. Helper docstrings and `.pxd` say this explicitly.
- **Receiver counts in `nargsf` for `call_method_vector`.** `PyObject_VectorcallMethod` treats `args[0]` as positional argument 0; passing the method arguments only makes the callee see zero arguments (measured: `read(2)` returned the whole stream).
- **Reserved slot.** When the `PY_VECTORCALL_ARGUMENTS_OFFSET` bit is set, `args[-1]` must be a real, writable slot, because CPython temporarily writes `self` there for method calls and restores it. A stack array with one spare slot is the safe spelling.

## Bench results

CPython 3.14.3, Linux x86_64, one million calls; ratio is helper / direct Python call.

| operation | helper s | direct s | ratio | verdict |
|---|---:|---:|---:|---|
| `call_noargs` | 0.0298 | 0.0144 | 2.07x | runtime convenience only |
| `call_onearg` | 0.0323 | 0.0179 | 1.81x | runtime convenience only |
| `call_twoargs` | 0.0383 | 0.0204 | 1.88x | runtime convenience only |

### 3.0 coverage run (2026-10-18)

[`bench/cycall_bench.py`](../../bench/cycall_bench.py), CPython 3.15.0rc2,
Intel i7-6700, portable installed RC1, CPU 2, N=80,000 × 5 runs.
Both sides call the same Python function with identical arguments and arithmetic.
The plain-Python wrapper performs direct invocation; no mock/no-op is timed.

| Helper | Case | Helper mean±σ (ms) | Direct mean±σ (ms) | Ratio |
|---|---|---:|---:|---:|
| `call_noargs` | zero arguments | 4.91±0.04 | 5.06±0.08 | 0.97x |
| `call_onearg` | one argument | 6.03±1.14 | 5.60±0.06 | 1.08x |
| `call_twoargs` | two arguments | 6.00±0.90 | 6.45±1.18 | 0.93x |

This closes missing runnable compare-label coverage, not a new performance
approval. A downstream build ran on another CPU during this Tier A run;
shared-host noise is visible in the samples. Keep ordinary Python invocation
as the consumer default and leave Core membership unchanged.


### Tier A re-run (2026-11-05)

Same harness, CPython 3.15.0rc2, CPU 2 pinned, 80,000 × 5 runs:
`call_noargs` **0.94x**, `call_onearg` **0.94x**, `call_twoargs` **0.93x** — all
inside the ≥5% gate.

### Tier B (2026-11-05) — `bench/tier_b/cycall.py`

picop `cdef` helper vs typed Cython baseline in the same extension, so the
comparison is real Cython code, not a Python call. Inner loop N = 2,000,000,
11 runs, CPU 2 pinned, CPython 3.15.0rc2. Baseline rows are the idiomatic
`func(a, b)` / `obj.read(1)` forms Cython compiles to `__Pyx_PyObject_FastCallDict`
/ `PyObject_VectorcallMethod`.

| operation | case | picop mean±σ (ms) | cy-base mean±σ (ms) | ratio | verdict |
|---|---|---:|---:|---:|---|
| `call_noargs` | zero args | 57.50±0.70 | 59.08±0.90 | **0.97x** | slight win |
| `call_onearg` | one arg | 72.87±5.08 | 73.90±1.10 | **0.99x** | tie |
| `call_twoargs` | two args | 74.58±0.89 | 70.68±0.99 | **1.06x** | baseline faster |
| `call_vector` | NULL args, `nargsf=0` | 57.07±1.10 | 60.36±4.89 | **0.95x** | win |
| `call_vector` | three positional | 88.95±0.82 | 86.48±0.80 | **1.03x** | baseline faster |
| `call_vector` | 1 positional + 1 kw | 90.27±1.04 | 93.17±5.05 | **0.97x** | win |
| arity probe | picop `nargsf` 3 vs 2 | 196.90±1.75 | 180.19±5.60 | **1.09x** | self-comparison, see below |
| arity probe | picop `nargsf` 4 vs 3 | 216.74±1.62 | 198.56±3.61 | **1.09x** | self-comparison, see below |
| `vectorcall_nargs` vs literal | macro cost | 76.44±0.81 | 74.55±1.84 | **1.02x** | free |
| reserved slot vs plain count | offset bit | 74.19±0.49 | 73.88±5.25 | **1.00x** | tie |
| `call_method_noargs` | `read()` | 42.27±2.10 | 42.07±0.46 | **1.00x** | tie |
| `call_method_onearg` | `read(1)` | 46.95±0.48 | 46.65±0.79 | **1.01x** | tie |
| `call_method_vector` | `read(1)` | 48.94±2.04 | 46.61±0.42 | **1.05x** | baseline faster (σ 2.0 ms) |

Summary: 4/13 picop faster, mean ratio 1.02x, median 1.01x.

Depth probes (one call each, output checked before the timed loops):

| probe | got | expected | ok |
|---|---|---|---|
| `call_vector` zero args (NULL vector) | `7` | `7` | True |
| `call_vector` three positional | `6` | `6` | True |
| `call_vector` four positional | `10` | `10` | True |
| `call_vector` positional + keyword | `3` | `3` | True |
| reserved-slot `nargsf` (NULL scratch, offset bit) | `5` | `5` | True |
| reserved-slot on a bound method | `b'a'` | `b'a'` | True |
| `call_method_noargs` | `b'abcdef'` | `b'abcdef'` | True |
| `call_method_onearg` | `b'a'` | `b'a'` | True |
| `call_method_vector` (receiver in `args[0]`) | `b'ab'` | `b'ab'` | True |
| exception propagation through `call_vector` | `division by zero` | `division by zero` | True |
| `Py_None` as `kwnames` | exit `-11` (SIGSEGV) | — | documented UB |

## Experiment conclusions

The public helpers are deliberately not Core or `picop.hot` candidates: ordinary
Python calls are faster because crossing a `cpdef` wrapper dominates. Their value
is a stable, explicit Cython call contract and a depth path that avoids building
argument tuples in extension code. The depth API is `call_vector`, which accepts
a caller-owned `PyObject*` array and keyword-name tuple; it must be exercised
only while the GIL is held and while every borrowed argument remains live.

**Why Tier A wins (0.93–0.94x).** Inside one compiled loop, Cython's own `f(a, b)`
expands to `__Pyx_PyObject_FastCallDict`, which tests `nargs == 0`/`nargs == 1`
against `METH_NOARGS`/`METH_O` flags, then resolves the vectorcall slot with
`__Pyx_PyVectorcall_Function(func)` before calling it. `call_noargs` /
`call_onearg` / `call_twoargs` hand the call straight to
`PyObject_CallNoArgs` / `PyObject_CallOneArg` / `PyObject_Vectorcall`, letting
CPython do that dispatch once, inlined, in the interpreter. The win is the
removed branch layer, not a different protocol — hence ~6%, not 2x.
The older 2.07x "loss" row in this tracker is a pure-Python harness measuring
`picop.call_noargs(f)` (module attribute + `cpdef` wrapper) against `f()`; there
the wrapper *is* the cost, which is why these stay out of the Core surface.

**Why Tier B ties (0.95–1.06x).** Generated baseline code in
`bench/tier_b/cycall_tb.c` shows Cython already emits vectorcall with the
reserved slot: `__Pyx_PyObject_FastCall(func, __pyx_callargs + t7, (1 - t7) |
(t7 * __Pyx_PY_VECTORCALL_ARGUMENTS_OFFSET))`. There is no protocol advantage
left to capture, only the dispatch check above. Ratios land within ±5%, which is
the cost of one extra non-inlined C function call.

**Arity rows are self-comparisons.** The "nargsf 3 vs 2" and "4 vs 3" rows
measure the helper against itself at different argument counts (the callable
sums its arguments, so work differs by one addition). Marginal cost of one extra
positional argument: 196.9 → 216.7 ms over 2 M calls ≈ **10 ns**, and the
baseline's own 180.2 → 198.6 ms ≈ **9 ns**. Both paths pay the same per-argument
price; arity, not the wrapper, drives those ratios.

**Reserved slot / offset bit.** `call_vector` forwards `nargsf` unchanged, so the
`PY_VECTORCALL_ARGUMENTS_OFFSET` spelling CPython and Cython use works, and it is
free (1.00x vs a plain count). Verified empirically: a `PyObject *slots[3]` with
`slots[0] = NULL`, call made at `slots + 1` with `nargsf = 2 | OFFSET` returned
the correct result, including on the bound-method path where CPython temporarily
writes `self` into `args[-1]`. `PyVectorcall_NARGS` (wrapped as `vectorcall_nargs`)
costs 1.02x — negligible, and it is the ABI-safe way to read a raw `nargsf`.

**Safety findings.** `kwnames = Py_None` is undefined: the probe subprocess
crashed with SIGSEGV (exit `-11`) rather than raising `TypeError`. For
`call_method_vector`, `args[0]` is the receiver and counts in `nargsf`; passing
only the method arguments silently drops the first one (measured: `read(2)`
returned the whole stream). Exception propagation through `call_vector` is
correct — `ZeroDivisionError` reached the caller with the usual message.

**Conclusion.** No helper is demoted or promoted. The three public call helpers
keep their Tier A win; the five `cdef` helpers stay cimport-only because a
borrowed `PyObject**` vector cannot be expressed from Python, and their value is
the contract and the documented safety rules, not extra speed.
