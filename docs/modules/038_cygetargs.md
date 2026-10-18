# cygetargs

| Field | Value |
|-------|--------|
| Status | present (cimport) |
| Maps to | `cpython.getargs` |
| Sources | `src/cypy/cygetargs.pxd` |
| Surface | cimport only |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

Varargs argument parsers for Cython extension code. Not wrappable as public Python helpers.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| PyArg_ParseTuple / AndKeywords / Parse / UnpackTuple | cimport | re-export extern |
| VaParse* | — | REJECTED as duplicate (va_list; use Parse*) |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| ParseTuple / AndKeywords / Parse / UnpackTuple | APPROVED (cimport) | ABI present; Cython call sites |
| VaParse* | REJECTED | va_list twin; no extra value |
| public cpdef | REJECTED | cannot wrap C varargs from Python |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-07-21 — Phase 4 Tier B n/a |
| Next action | — |

## Decision log

| Function | Probe | Decision | Iteration |
|----------|-------|----------|-----------|
| ParseTuple | ctypes OK | APPROVED (cimport) | 1 |
| public wrap | varargs | REJECTED | 1 |

## Bench notes

- n/a (cimport-only)

## Bench results

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| — | cimport-only | — | — | n/a | — | n/a (cimport) |

### Tier B (Cython baseline)

| operation | case | cypy mean±σ | p99 | ratio | note |
|-----------|------|-------------|-----|-------|------|
| — | — | — | — | n/a (cimport) | No public `cpdef` hot path — cimport-only surface; Tier B harness not applicable |

**Tier B takeaway:** n/a (cimport) — no public helper to compare against a typed Cython baseline.

## Experiment conclusions

**Tier B:** n/a (cimport).

| Topic | Finding |
|-------|---------|
| Why cimport | C varargs / format strings cannot be wrapped as meaningful `cpdef` without inventing a DSL |
| ABI | `PyArg_ParseTuple` / `AndKeywords` / `UnpackTuple` present; call from cdef with typed out-params |
| GIL / safety | Parsers run under the GIL; failed parse sets exceptions — do not call with stolen refs into out slots |
| Ownership | Successful parse INCREFs owned out-objects per format; caller owns them like any C-API parse |
| VaParse | va_list twins rejected as duplicates — use Parse* from Cython |
| Prefer | Keep surface cimport-only; Python call sites use normal `*args`/`**kwargs` |

## Done when

- [x] Try-all evidence + cimport + QUEUE
