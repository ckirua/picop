# cylock

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython/lock.h` (3.14) / `cpython/pylock.h` (3.15) — `PyMutex` |
| Sources | `src/picop/cylock.pxd` |
| Surface | cimport only |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

`PyMutex` is the free-threading primitive CPython uses for every internal lock: a
one-byte struct, `typedef struct PyMutex { uint8_t _bits; } PyMutex;`, with
`PyMutex_Lock`, `PyMutex_Unlock`, `PyMutex_IsLocked` and inline `_PyMutex_*`
fast paths that CAS the byte before falling back to the exported function. It is
not a Python object and there is nothing to wrap for Python callers — a
`PyMutex` is always a value the extension author declares.

The value of the Order is discoverability plus a documented ownership contract.
Extensions that hand-roll `cdef extern from "Python.h": struct PyMutex ...` get the
struct shape wrong (the 3.14 header says `uint8_t _bits`; a `uint32_t` guess
corrupts the adjacent struct field), and picop already carries a documented rule
that cimport-only surfaces must be embedding footguns worth writing down. Locking
the wrong mutex, or unlocking one you do not own, is silent corruption in a
`Py_GIL_DISABLED` build, so the surface ships with a `docs/SAFETY.md` entry rather
than being declined.

`cython.critical_section` covers the common "protect one object" case; `cylock`
is for the cases Cython cannot express — a mutex stored in a C struct, a mutex
shared with a library, or a lock held across a section that already released the
GIL.

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| `PyMutex` | C-API | approved | cimport | one byte (`uint8_t _bits`); contents are not public API — the field is declared only so Cython can size a stack-local |
| `mutex_init` | picop | approved | cimport | `memset` to zero; zero is the unlocked state |
| `mutex_lock` / `mutex_unlock` | C-API | approved | cimport | `noexcept` inline wrappers over `PyMutex_Lock` / `PyMutex_Unlock`, callable from `nogil` blocks |
| `mutex_is_locked` | C-API | approved | cimport | `bint` over `PyMutex_IsLocked` |
| `_PyMutex_Lock` / `_PyMutex_Unlock` | C-API | internal | — | `Python.h` redefines the public names to these inline CAS fast paths; wrappers pick them up automatically |
| `PyLock` | C-API | internal | — | parked lock object for the free-threaded runtime; not exposed |
| `critical_section` | Cython | existing | — | Cython already provides `cython.critical_section`; `cylock` is for locks Cython cannot express |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| `mutex_lock` / `mutex_unlock` / `mutex_is_locked` | SHIPPED | `noexcept` `nogil` inline wrappers; no Python-visible surface, so no Tier A/Tier B harness |
| `mutex_init` | SHIPPED | zero-initialises a stack-local `PyMutex`; CPython guarantees zero is unlocked |
| typed `PyMutex` barrel cimport | SHIPPED | `from picop cimport PyMutex, mutex_lock, …` verified in `examples/cimport_ext/demo.pyx` |
| `PyLock` / parked-thread internals | REJECTED | interpreter-owned; no stable ABI contract to wrap |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-11-06 — implemented, smoked against CPython 3.15 (GIL) and in the CI matrix |
| Next action | extend only if a header diff adds a lock API (e.g. a public `PyLock` type) |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| mutex helpers | barrel cimport helps free-threaded extensions | n/a (cimport, no harness) | compiles through the barrel in 3.14/3.15, GIL and `Py_GIL_DISABLED`; cross-thread lock state observed | APPROVED (cimport) | 1 |
| `PyLock` wrapper | expose the parked-lock object | — | interpreter-internal, no public contract | REJECTED | 1 |

## Bench notes

- No harness: the primitives are C-level and are not callable from Python.
- Evidence is the cimport smoke, not a ratio: `scripts/smoke_barrel_cimport.sh`
  (`smoke OK`) locks a stack-local mutex inside a `nogil` block, then holds a
  module-level mutex in one thread while another thread reads
  `shared_is_locked()` — True while held, False after release.
- Gate: [`docs/README.md`](../README.md) — not applicable, no public helper.

## Bench results

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| — | cimport-only | — | — | — | — | n/a (cimport, no harness; smoke OK) |

### Tier B (Cython baseline)

| operation | case | cypy mean±σ | p99 | ratio | note |
|-----------|------|-------------|-----|-------|------|
| — | — | — | — | n/a (cimport) | No public `cpdef` hot path — `cdef inline` wrappers only, so there is no Python-side call to compare |

**Tier B takeaway:** n/a (cimport) — the helpers are inlined C calls; the measured
cost is the CPython `PyMutex` CAS itself, identical to a hand-written extern.

## Experiment conclusions

`cpython/lock.h` (3.14) / `cpython/pylock.h` (3.15) is the last unwrapped
CPython header with a plausible module, and Cython ships no `pylock.pxd`, so
every extension that wants a typed mutex declares the struct itself. The
decision hinges on ownership: a `PyMutex` is a value the extension author
declares, so picop can only ever borrow `PyMutex *`. That is a stable contract
for a lock — the caller owns the storage for the whole critical section — but it
is not refcount-safe in the `cy*` sense, and the struct contents are explicitly
"not part of the public API", so the field is declared only to size a stack
local and is never read or written by picop code.

| Topic | Finding |
|-------|---------|
| Ownership | mutex storage is caller-declared; picop borrows `PyMutex *` for the call only |
| Free-threading / GIL | the real win is under `Py_GIL_DISABLED`; the wrappers still work on GIL builds (`PyMutex_Lock` is exported in both), so the module is not dead weight |
| ABI | `Python.h` redefines `PyMutex_Lock` to the inline `_PyMutex_Lock` CAS fast path; declaring the public name picks the fast path automatically |
| Struct shape | the tracker's original `uint32_t bits` note was wrong — CPython uses one `uint8_t`, and a wrong declaration corrupts neighbouring struct fields |
| Safety | unlocking a mutex you do not own is silent corruption; shipped with a `docs/SAFETY.md` entry |
| Threshold | `cython.critical_section` covers the single-object case; `cylock` is for locks Cython cannot express |

**Decision:** ship as a cimport-only module. No Tier A ratio exists because there
is no Python-callable helper; the smoke run is the acceptance gate.

## Done when

- [x] Full inventory vs mapped include
- [x] Every row has workflow status
- [x] Lifecycle + next action filled
- [x] `src/picop/cylock.pxd` present and wired into the package barrel (`__init__.pxd`)
- [x] `docs/SAFETY.md` entry on borrowed `PyMutex *` and unlock ownership
- [x] `scripts/smoke_barrel_cimport.sh` asserts lock/unlock/is-locked semantics across threads
