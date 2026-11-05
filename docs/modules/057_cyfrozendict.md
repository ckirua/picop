# cyfrozendict

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.frozendict` / `cpython/dictobject.h` (CPython **3.15+**) |
| Sources | `src/picop/cyfrozendict.pxd` (whole surface, like `cydict`), `src/picop/cyfrozendict.pyx` (docstring stub), `src/picop/cyfrozendict.pyi`, `src/picop/cyfrozendict_shim.h` |
| Surface | public + cimport |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

`frozendict` is the first new container type in CPython 3.15, and Cython's own
`cpython.frozendict` include ships only checks plus a constructor that
silently backports to `dict` on older ABIs. picop ships the same primitives
with an **explicit** 3.14 behaviour (checks `False`, constructors raise
`NotImplementedError`) instead of handing back a mutable `dict` under a
"frozen" name. The value is not the allocation — it is the *type gate*: a
frozendict is not a `dict` subtype, so every typed `dict_*` helper in `cydict`
is wrong for it, and callers need `anydict_*` instead.

## Inventory

Complete mapped surface (`cpython/dictobject.h` frozendict block, plus
everything Cython's `frozendict.pxd` exposes). No skim.

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| `PyFrozenDict_Type` | C-API | type object | — | reached through the checks; not exported |
| `PyFrozenDict_Check` | C-API | macro (`PyObject_TypeCheck`) | `frozendict_check` | subtype-OK: `frozendict` **is** subclassable |
| `PyFrozenDict_CheckExact` | C-API | macro (`Py_IS_TYPE`) | `frozendict_check_exact` | exact type only |
| `PyAnyDict_Check` | C-API | macro | `anydict_check` | dict **or** frozendict, subtypes included |
| `PyAnyDict_CheckExact` | C-API | macro | `anydict_check_exact` | excludes `dict` subclasses such as `defaultdict` |
| `PyFrozenDict_New(iterable)` | C-API | function | `frozendict_new` | `NULL` iterable → empty frozendict (C path; `frozendict_new(None)` raises `TypeError`, like the builtin) |
| — (`NULL` iterable) | used-by | — | `frozendict_empty` | zero-arg fast path, no iterable build |
| `PyDict_GET_SIZE` | C-API | static inline (asserts `PyAnyDict_Check`) | `anydict_len` | shared dict layout; valid on frozendict |
| `PyDict_GetItem` / `PyDict_Contains` | C-API | function | — | work on frozendict (borrowed return); not exported — subscript is already fast |
| `PyDict_Copy` / `PyDict_Merge` / `PyDict_SetItem` | used-by | function | — | **REJECTED**: reject frozendict (measured `SystemError`, see conclusions) |
| `PyFrozenDictObject` / `_PyFrozenDictObject_CAST` | internal | struct (`PyDictObject` + `ma_hash`) | — | not reachable; layout evidence only |

Cython's `cpython.frozendict` include declares exactly the five checks /
constructor symbols above (with a `dict` fallback). Nothing in that include is
unmapped.

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| `frozendict_check` | APPROVED | 0.39–0.53x vs `isinstance(x, frozendict)` |
| `frozendict_check_exact` | APPROVED | 0.50x vs `type(x) is frozendict` |
| `anydict_check` | APPROVED | 0.27–0.32x; no cheap builtin equivalent for "dict or frozendict" |
| `anydict_check_exact` | APPROVED | 0.40–0.45x vs a two-`type` compare |
| `frozendict_new` | APPROVED (API) | tie from a `dict` (0.97–1.01x, allocation-bound), 0.51x when re-wrapping a frozendict; also the only frozendict "copy" path |
| `frozendict_empty` | APPROVED | 0.77x vs `frozendict()` |
| `anydict_len` | APPROVED | 0.49–0.53x vs `len(...)`; one guard buys the unchecked macro path |
| `PyDict_Copy` wrapper | REJECTED | `SystemError: bad argument to internal function` on a frozendict |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 0 |
| Last pass | 2026-11-05 — full inventory, Tier A try-all + depth probes, Tier B harness added |
| Next action | Order 058 `cysentinel` (`cpython/sentinelobject.h`); revisit if CPython ships a public frozendict copy API |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| `frozendict_check` | macro check beats the builtin `isinstance` lookup | `bench/cyfrozendict_bench.py` | 0.39–0.53x | APPROVED | 0 |
| `anydict_check` | dict-or-frozendict gate is expensive in Python | same | 0.27–0.32x | APPROVED | 0 |
| `frozendict_new` | direct C ctor beats builtin `frozendict(...)` | same | 0.97–1.01x dict, 0.51x frozendict | APPROVED (API) | 0 |
| `frozendict_empty` | `PyFrozenDict_New(NULL)` beats a builtin call | same | 0.77x | APPROVED | 0 |
| `anydict_len` | guarded `PyDict_GET_SIZE` beats `len()` dispatch | same | 0.49–0.53x | APPROVED | 0 |
| copy via `PyDict_Copy` | dict-family copy helpers accept frozendict | throwaway probe extension | `SystemError`, no ratio | REJECTED | 0 |

## Bench notes

- Harness: `bench/cyfrozendict_bench.py` — see [`bench/BENCH.md`](../../bench/BENCH.md)
- Tier B harness: `bench/tier_b/cyfrozendict.py` (`cyfrozendict_tb.pyx`)
- **Mandatory:** paste **Bench results** + **Experiment conclusions** into **this file** after every measuring pass — **no skip** (PR-only is not enough)
- Gate: [`docs/README.md`](../README.md) (mean ratio ≤ 0.95; cimport demote allowed)
- Env: CPython 3.15.0rc2 (GIL build), Linux x86_64, Tier A N=80,000 × RUNS=5; Tier B inner loop N=2,000,000

## Bench results

### Tier A (public helper vs plain Python)

| operation | case | picop mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| `frozendict_check` | frozendict hit | 2.01±0.03ms | 2.05ms | **0.44x** | 0.39x | APPROVED |
| `frozendict_check` | dict miss | 2.23±0.07ms | 2.33ms | **0.39x** | 0.40x | APPROVED |
| `frozendict_check_exact` | hit | 2.40±0.51ms | 3.23ms | **0.57x** | 0.74x | APPROVED |
| `anydict_check` | frozendict | 2.24±0.26ms | 2.55ms | **0.30x** | 0.33x | APPROVED |
| `anydict_check` | dict | 3.03±0.96ms | 3.87ms | **0.47x** | 0.53x | APPROVED |
| `anydict_check_exact` | frozendict | 2.13±0.14ms | 2.36ms | **0.40x** | 0.44x | APPROVED |
| `anydict_check_exact` | dict | 2.07±0.02ms | 2.09ms | **0.41x** | 0.34x | APPROVED |
| `frozendict_new` | from dict (4 items) | 9.31±0.45ms | 10.07ms | 0.97x | 0.93x | tie — API-clarity keep |
| `frozendict_new` | from frozendict | 2.23±0.03ms | 2.25ms | **0.51x** | 0.51x | APPROVED |
| `frozendict_empty` | no iterable | 4.67±0.04ms | 4.73ms | **0.75x** | 0.65x | APPROVED |
| `anydict_len` | frozendict, 4 items | 2.15±0.03ms | 2.20ms | **0.55x** | 0.55x | APPROVED |
| `anydict_len` | dict, 4 items | 2.13±0.04ms | 2.18ms | **0.51x** | 0.43x | APPROVED |

12/12 picop faster, 11/12 pass the ≥5% gate, mean ratio 0.52x, median 0.49x.
`frozendict_new` from a plain `dict` sits at 0.97–1.01x across runs —
allocation-bound, no measurable win.

### Tier B (Cython baseline)

| operation | case | picop loop | cython baseline | ratio | p99× | note |
|-----------|------|------------|-----------------|-------|------|------|
| `frozendict_check` | hit | 3.08±0.04ms | 3.28±0.38ms | 0.94x | 0.80x | ~tie — Cython already emits the same `PyObject_TypeCheck` |
| `frozendict_check` | dict miss | 8.36±0.82ms | 7.97±0.48ms | 1.05x | 1.08x | baseline marginally faster |
| `frozendict_check_exact` | hit | 2.68±0.03ms | 4.94±0.12ms | **0.54x** | 0.53x | win |
| `anydict_check` | dict | 3.16±0.00ms | 4.36±0.08ms | **0.73x** | 0.71x | win |
| `anydict_check` | frozendict | 3.96±0.25ms | 5.29±0.03ms | **0.75x** | 0.82x | win |
| `anydict_check_exact` | frozendict | 2.55±0.00ms | 5.61±0.05ms | **0.45x** | 0.45x | win |
| `anydict_check_exact` | dict | 2.61±0.05ms | 5.64±0.24ms | **0.46x** | 0.44x | win |
| `anydict_len` | frozendict | 3.73±0.08ms | 7.80±0.48ms | **0.48x** | 0.45x | win |
| `anydict_len` | dict | 3.17±0.02ms | 7.71±0.62ms | **0.41x** | 0.37x | win |

`frozendict_new` / `frozendict_empty`: n/a — alloc-dominated (see
[`OPS_INVENTORY_TIERB.md`](../OPS_INVENTORY_TIERB.md)).

## Experiment conclusions

- **Subtype / ABI.** `frozendict` is *not* a `dict` subclass:
  `isinstance(fd, dict)` is `False` and `PyDict_Check(fd)` is `False`, so
  `dict_check` / `dict_len` / `dict_get` (typed `dict` parameters) raise
  `TypeError` on a frozendict. Subclassing **is** allowed
  (`class FD(frozendict)` works), which is why `frozendict_check` uses
  `PyObject_TypeCheck` and the `_exact` sibling exists.
- **Layout sharing.** `PyFrozenDictObject` is `PyDictObject` plus a
  `Py_hash_t ma_hash`, and `PyDict_GET_SIZE` / `PyDict_GetItem` /
  `PyDict_Contains` assert `PyAnyDict_Check`, not `PyDict_Check`. That is the
  entire reason `anydict_len` is safe on a frozendict: the read path is the
  same dict layout, and the hash is computed once and cached in `ma_hash`
  (equal frozendicts hash equal, and a frozendict compares equal to a plain
  dict with the same items).
- **Safety footgun (measured).** `PyDict_Copy(fd)` returns
  `SystemError: Objects/dictobject.c:4542: bad argument to internal function`
  and `PyDict_Merge(fd, …)` fails the same way — mutation helpers reject
  frozendicts. `frozendict_new(fd)` is the copy path, but it short-circuits:
  `frozendict_new(fd) is fd` (a refcount bump on the same object). Callers
  needing a genuinely new object must build from an iterable.
- **Version gate / ownership.** `frozendict` needs `PY_VERSION_HEX >=
  0x030F0000`. Cython 3.3.1's include backports to `dict` on 3.14; picop's
  shim keeps the contract honest: checks `False`, constructors raise
  `NotImplementedError`, so no mutable `dict` escapes under a frozen name.
  Returns from `frozendict_new` / `frozendict_empty` are new references owned
  by the caller; the `NULL`-iterable path allocates nothing extra.
- **Free-threading.** The module is `freethreading_compatible=True`:
  frozendicts are immutable after construction and every constructor builds
  its own object, so the check helpers touch no shared mutable state.
- **Threshold.** The `anydict_len` guard (one `PyAnyDict_Check`) is free
  against `len()` dispatch (0.49–0.53x), so it stays. Tier B shows
  `frozendict_check` is already the exact macro Cython emits for
  `isinstance(..., frozendict)` — a genuine tie, kept for API clarity; the
  `_exact` variants are where the win is real.

## Done when

- [x] Full inventory vs mapped include (or declared custom surface)
- [x] Every row has workflow status
- [x] Lifecycle + next action filled
- [x] APPROVED / APPROVED (cimport) rows have decision-log evidence
- [x] REJECTED rows have policy or measured why
- [x] Present measuring: try-all **and** depth checklist in **this tracker's** Experiment conclusions (**no skip**)
- [x] **Bench results** table filled in **this file** (not only PR)
- [x] Public PEP 257 one-liners in `cyfrozendict.pyi`; `.pxd` lean
