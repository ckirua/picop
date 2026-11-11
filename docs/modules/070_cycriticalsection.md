# cycriticalsection

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `critical_section.h` (CPython 3.14/3.15) |
| Sources | `src/picop/cycriticalsection.pxd`, `src/picop/cycriticalsection_shim.h` |
| Surface | cimport only |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

Critical sections are CPython's object-scoped synchronization mechanism for free-threaded builds. The wrappers expose explicit begin/end calls for control flow that cannot be expressed as a lexical block, and mutex-based variants for sections associated with caller-owned `PyMutex` values. In GIL builds the same entry points are no-ops, matching CPython semantics. This is cimport-only: stack buffers and explicit lock lifetimes are Cython-level tools, not suitable Python-callable APIs. For ordinary lexical protection of one or two objects, use Cython's `with cython.critical_section(...)` syntax.

## Inventory

Full surface of `critical_section.h` for CPython 3.14/3.15.

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| `PyCriticalSection_Begin` | C-API | function | cimport `cs_begin` | Starts a section for one object using caller-provided aligned buffer. |
| `PyCriticalSection_End` | C-API | function | cimport `cs_end` | Ends the corresponding single-object section. |
| `PyCriticalSection_BeginMutex` | C-API | function | cimport `cs_begin_mutex` | Starts a section guarded by a borrowed caller-owned mutex. |
| `PyCriticalSection2_Begin` | C-API | function | cimport `cs2_begin` | Starts a section for two objects. |
| `PyCriticalSection2_End` | C-API | function | cimport `cs2_end` | Ends the corresponding two-object section. |
| `PyCriticalSection2_BeginMutex` | C-API | function | cimport `cs2_begin_mutex` | Starts a section guarded by two borrowed mutexes. |
| `Py_BEGIN_CRITICAL_SECTION` | C-API | block macro | — | C-only; the equivalent lexical block is already expressed by Cython's `with cython.critical_section(...)` syntax. |
| `Py_BEGIN_CRITICAL_SECTION_MUTEX` | C-API | block macro | — | C-only; no picop export; mutex-specific lexical block macro. |
| `Py_BEGIN_CRITICAL_SECTION2` | C-API | block macro | — | C-only; two-object lexical block is already expressed by Cython's `with cython.critical_section(a, b)` syntax. |
| `Py_BEGIN_CRITICAL_SECTION2_MUTEX` | C-API | block macro | — | C-only; no picop export; two-mutex lexical block macro. |
| `Py_END_CRITICAL_SECTION` | C-API | block macro | — | C-only closing delimiter, used with `Py_BEGIN_CRITICAL_SECTION`; no picop export. |
| `Py_END_CRITICAL_SECTION2` | C-API | block macro | — | C-only closing delimiter, used with `Py_BEGIN_CRITICAL_SECTION2`; no picop export. |
| `PyCriticalSection` | C-API | private struct layout | — | Private release-changing layout is deliberately not redeclared; shim uses an aligned buffer and compile-time size check instead. |
| `PyCriticalSection2` | C-API | private struct layout | — | Private release-changing layout is deliberately not redeclared; shim uses an aligned buffer and compile-time size check instead. |
| `critical_sections_enabled` | picop | function | cimport | Reports whether this build enables critical-section locking (1/0); does not correspond to a separate header symbol. |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| `cs_begin` / `cs_end` | APPROVED (cimport) | Explicit lifetime supports non-block control flow while keeping stack storage and pairing under the Cython caller's control. |
| `cs_begin_mutex` | APPROVED (cimport) | Supports critical sections guarded by a caller-owned mutex where Cython's object syntax is insufficient. |
| `cs2_begin` / `cs2_end` | APPROVED (cimport) | Exposes CPython's two-object section for explicit non-lexical lifetimes. |
| `cs2_begin_mutex` | APPROVED (cimport) | Supports two caller-owned mutexes without exposing a Python-callable locking API. |
| `critical_sections_enabled` | APPROVED (cimport) | Lets compiled callers distinguish GIL and free-threaded behavior without creating public Python surface. |
| `Py_BEGIN_CRITICAL_SECTION`, `Py_BEGIN_CRITICAL_SECTION_MUTEX`, `Py_BEGIN_CRITICAL_SECTION2`, `Py_BEGIN_CRITICAL_SECTION2_MUTEX`, `Py_END_CRITICAL_SECTION`, `Py_END_CRITICAL_SECTION2` | REJECTED | C-only block delimiters; Cython's `with cython.critical_section(...)` already expresses object-scoped lexical sections, and macros cannot be exposed as Cython callables. |
| `PyCriticalSection` / `PyCriticalSection2` layouts | REJECTED | Private ABI layouts can change between CPython releases; the shim's aligned buffers and compile-time size check avoid redeclaring them. |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-11-11 — full header inventory, cimport scope decisions, and Tier B measurements on CPython 3.15t recorded |
| Next action | run the gates and merge; revisit if CPython changes the private section layout |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| `cs_begin` / `cs_end` | explicit object section calls are useful in compiled non-lexical control flow | `bench/tier_b/cycriticalsection.py` | 77.18±0.76 ms vs 81.84±0.58 ms lexical block (0.94x) | APPROVED (cimport) — stack-only scope; no Python boundary | 1 |
| `cs_begin_mutex` | mutex-guarded object section covers a case unavailable through Cython's object syntax | `bench/tier_b/cycriticalsection.py` | 31.06±1.79 ms vs 19.25±0.20 ms bare mutex pair (1.61x) | APPROVED (cimport) — expressiveness over speed; cost documented | 1 |
| `cs2_begin` / `cs2_end` | explicit two-object section supports non-lexical control flow | `bench/tier_b/cycriticalsection.py` | not benched separately; same call shape as the measured `cs2_begin_mutex` / `cs2_end` pair | APPROVED (cimport) | 1 |
| `cs2_begin_mutex` | two-mutex form has a distinct caller need | `bench/tier_b/cycriticalsection.py` | 171.22±11.74 ms vs 154.70±1.14 ms sequential pairs (1.11x) | APPROVED (cimport) — suspend/resume semantics justify the overhead | 1 |
| Critical-section block macros | a Cython-callable wrapper is useful | — | Cython already provides lexical object critical sections | REJECTED | 0 |
| Private struct layouts | redeclaring layout would simplify caller buffers | — | Private layout creates release ABI risk; shim buffer avoids it | REJECTED | 0 |
| `critical_sections_enabled` | build-mode query clarifies no-op versus locking semantics | `bench/tier_b/cycriticalsection.py` | 0.00 ms over 2,000,000 iterations (constant-folded by the C compiler) | APPROVED (cimport) | 1 |

## Bench notes

- Tier B harness: [`bench/tier_b/cycriticalsection.py`](../../bench/tier_b/cycriticalsection.py)
- Tier A: n/a (no public barrel export); the measured rows are the Tier B table above.
- These entry points have no Python-visible surface, so Tier A has no public operation to compare.

## Bench results

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|-------|---------|
| `cs_begin` / `cs_end` around a dict store | vs `with cython.critical_section(d)` | 77.18±0.76 ms | 78.12 ms | **0.94x** | 0.95x | explicit pair 6% faster than the lexical block |
| `cs_begin_mutex` / `cs_end` around a counter | vs `mutex_lock` / `mutex_unlock` | 31.06±1.79 ms | 33.61 ms | **1.61x** | 1.73x | slower: suspend/resume bookkeeping, see conclusions |
| `cs2_begin_mutex` / `cs2_end` around a two-dict swap | vs two sequential lock/unlock pairs | 171.22±11.74 ms | 191.15 ms | **1.11x** | 1.22x | slightly slower; the pair is the cheaper raw primitive |
| `critical_sections_enabled()` in a hot loop | vs `sys._is_gil_enabled()` | 0.00±0.00 ms | 0.00 ms | **0.00x** | 0.00x | C folds the inline query away; guard is free |

Env: CPython 3.15.0rc2 free-threaded (`PYTHON_GIL=0`), Linux, N=2,000,000, 5 runs, warmup 0. Harness: `bench/tier_b/cycriticalsection.py` (`bash bench/tier_b/run.sh cycriticalsection`). Ratio is cypy/baseline, so below 1.0 means picop is faster.

## Experiment conclusions

Critical sections are no-ops when the GIL is enabled; on free-threaded builds they provide synchronization, so callers must not treat `critical_sections_enabled()` as a lock or assume the protected operation is serialized on every build. Sections support nesting through CPython's suspend/resume behavior: entering a nested section suspends the outer protection as required and leaving the inner section resumes it, rather than simply recursively holding the same object lock. Mutex-based sections matter when protection must be tied to a caller-owned `PyMutex`, including state not naturally represented by a Python object critical section; callers must ensure borrowed mutexes outlive each section and obey the mutex's locking contract. The CPython section struct layouts are private and release-changing. Exposing or duplicating them in Cython declarations would couple extensions to unstable ABI details; this implementation instead provides aligned stack buffers in the shim and checks their capacity at compile time. Tier B measurements on 3.15t show the object-scoped pair is marginally cheaper than Cython's lexical block (0.94x), while the mutex-guarded pair costs 1.61x a bare `mutex_lock` / `mutex_unlock` pair and the two-mutex form 1.11x two sequential pairs: a critical section has to register the guarded mutex on the thread state so nested sections can suspend and resume it, and that bookkeeping is the difference. Callers who only need a plain mutex should use `picop.cylock` directly; the critical-section wrappers are the right choice when they need CPython's suspend/resume nesting semantics or protection tied to a Python object rather than to a mutex they own. `critical_sections_enabled()` measures as 0.00 ms in a hot loop because the C compiler folds the inline query out, so build-mode guards add no per-iteration cost. Tier A comparison is impossible because this module has no public barrel export.

## Done when

- [x] Full inventory vs mapped include (`critical_section.h`, CPython 3.14/3.15)
- [x] Every row has workflow status
- [x] Lifecycle + next action filled
- [x] APPROVED / APPROVED (cimport) rows have decision-log evidence
- [x] REJECTED rows have policy or measured why
- [x] Experiment conclusions cover GIL behavior, nesting/suspend-resume, mutex use, and private-layout ABI risk
- [x] **Bench results** table filled in this file with measured Tier B results
- [x] No `.pyi` needed (cimport-only); `.pxd` lean
