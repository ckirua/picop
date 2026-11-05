# cylock

| Field | Value |
|-------|--------|
| Status | absent |
| Maps to | `cpython/pylock.h` (`PyMutex`) |
| Sources | — |
| Surface | cimport-only (candidate) |
| Tracker lifecycle | indexed (deferred) |
| Format | v2 |
| Indexed | full |

## Why

Order 063 scoped the free-threading lock primitives. `PyMutex` is a two-byte C
struct, not a Python object: `typedef struct PyMutex { uint32_t bits; } PyMutex;`
with `PyMutex_Lock`, `PyMutex_Unlock`, `PyMutex_IsLocked` and the inline
`_PyMutex_Lock`/`_PyMutex_Unlock` variants. There is nothing to wrap for Python
callers — a helper would only serve Cython extensions that already get these from
`Python.h`. The value is discoverability (a barrel cimport for a typed
`PyMutex *`), not speed, and picop's rule for cimport-only modules is that they
must be embedding footguns worth documenting. Locking the wrong mutex in a
free-threaded extension is exactly that kind of footgun, so the Order stays open
rather than being declined.

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| `PyMutex` | C-API | candidate | cimport | `uint32_t bits`; contents are not public API |
| `PyMutex_Lock` / `PyMutex_Unlock` | C-API | candidate | cimport | public functions |
| `PyMutex_IsLocked` | C-API | candidate | cimport | public function |
| `_PyMutex_Lock` / `_PyMutex_Unlock` | C-API | internal | — | inline fast paths |
| `PyLock` | C-API | internal | — | parked lock object for the free-threaded runtime |
| `critical_section` | Cython | existing | — | Cython already provides `cython.critical_section` |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| `PyMutex_Lock` / `Unlock` wrappers | DEFERRED | no Python-visible benefit; Cython callers use `critical_section` |
| typed `PyMutex *` barrel cimport | DEFERRED | would need a SAFETY entry on lock ownership |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 0 |
| Last pass | 2026-11-05 — header diff against CPython 3.15 headers |
| Next action | promote only with a named caller that needs typed mutexes in an extension |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| mutex helpers | barrel cimport helps free-threaded extensions | path or — | no harness; no measurable helper call | DEFERRED | 0 |

## Bench notes

- No harness: the primitives are C-level and are not callable from Python.
- Gate: [`docs/README.md`](../README.md) — not applicable, no public helper.

## Bench results

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| — | — | — | — | — | — | n/a (cimport-only, no harness) |

## Experiment conclusions

`cpython/pylock.h` is the last unwrapped header with a plausible module, and it is
unwrapped because Cython ships no `pylock.pxd`. The decision hinges on ownership:
a `PyMutex` is a value the extension author declares, so picop can only pass
pointers, which makes every call a borrowed-pointer contract rather than a
refcount-safe one.

| Topic | Finding |
|-------|---------|
| Ownership | mutex storage is caller-declared; picop would only borrow `PyMutex *` |
| Free-threading / GIL | useful only under `Py_GIL_DISABLED`; on GIL builds the wrappers are dead weight |
| ABI | struct contents are explicitly "not part of the public API" |
| Safety | a wrong unlock is silent corruption — needs a `docs/SAFETY.md` entry before shipping |
| Threshold | Cython's `critical_section` already covers the common case |

**Decision:** keep as an open, indexed Order. Do not ship until a concrete
extension need is named.

## Done when

- [x] Full inventory vs mapped include
- [x] Every row has workflow status
- [x] Lifecycle + next action filled
