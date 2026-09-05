# cyfileobject

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.fileobject` |
| Sources | `src/cypy/cyfileobject.pxd`, `.pyx`, `.pyi` |
| Surface | public |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

File FromFd / GetLine / Write helpers for Cython I/O.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| file_from_fd / getline / write_object / write_string | public | |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| all four | APPROVED (API) | I/O bridge; see benches |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
| Last pass | 2026-07-21 — Phase 4 Tier B |
| Next action | — |

## Bench notes

- Harness: [`bench/cyfileobject_bench.py`](../../bench/cyfileobject_bench.py)

## Bench results

Harness: [`bench/cyfileobject_bench.py`](../../bench/cyfileobject_bench.py) · smoke / ABI (getline loop raises EOFError in harness)

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| — | smoke + ABI | — | — | n/a | — | n/a (cimport) / smoke OK |
| file_from_fd | closefd paths | — | — | n/a | — | API smoke |
| file_getline | until EOF | — | — | n/a | — | harness EOFError — not Tier A |
| file_write_* | real file | — | — | n/a | — | API smoke |

### Tier B (Cython baseline)

| operation | case | cypy mean±σ | p99 | ratio | note |
|-----------|------|-------------|-----|-------|------|
| — | EOF getline | — | — | n/a | Unfair microbench (I/O / EOF) — same rationale as Tier A; no fair in-memory cdef-loop baseline |

**Tier B takeaway:** stay **n/a** — fileobject hot path is I/O-bound; Tier B would not inform extension authors beyond Tier A.

## Experiment conclusions

**Tier B:** n/a (unfair EOF/I/O microbench).

| Topic | Finding |
|-------|---------|
| Why no Tier A ratios | Harness `getline` loop hits EOFError at end-of-file; not a fair microbench vs Python `readline` |
| ABI / FILE* | Wraps CPython fileobject helpers over OS fds / `PyFile_*` — not raw stdio FILE* for public |
| Ownership / safety | `FromFd` takes ownership when `closefd` true; wrong closefd → fd double-close |
| GIL | I/O releases/reacquires per CPython file rules; do not hold borrowed file objects across threads casually |
| Prefer | Use as Cython I/O bridge; measure application-level I/O, not synthetic getline loops |

## Done when

- [x] Try-all + depth + benches + `.pyi`
