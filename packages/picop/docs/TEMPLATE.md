# cy{name}

<!-- File as docs/modules/NNN_cy{name}.md — NNN = QUEUE Order (001…055). -->

| Field | Value |
|-------|--------|
| Status | present / absent |
| Maps to | `cpython.{x}` / custom / `Python.h` |
| Sources | `src/cypy/cy{name}.*` or — |
| Surface | public / cimport / none |
| Tracker lifecycle | stub / indexed / implementing / measuring / decided |
| Format | v2 |
| Indexed | full / partial / none |

## Why

Rationale for this module’s scope (what we accelerate and what we leave out). Not a status flag.

## Inventory

Full surface for the mapped include (or custom module API). No skim.

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| … | cypy / C-API / used-by | cpdef / cdef / candidate | public / cimport / cdef / — | … |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| … | TODO / ONGOING / APPROVED / APPROVED (cimport) / REJECTED | … |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 0 |
| Last pass | YYYY-MM-DD — … |
| Next action | … |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| … | … | path or — | … | TODO / … | 0 |

## Bench notes

- Harness: `bench/cy{name}_bench.py` — see [`bench/BENCH.md`](../../bench/BENCH.md)
- **Mandatory:** paste **Bench results** + **Experiment conclusions** into **this file** after every measuring pass — **no skip** (PR-only is not enough)
- Gate: [`docs/README.md`](../README.md) (mean ratio ≤ 0.95; cimport demote allowed)
- Env: CPython …, platform …, GIL …, N/RUNS …

## Bench results

<!-- Paste timed table from harness here after measuring pass -->

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| … | … | … | … | … | … | … |

## Experiment conclusions

<!-- Smoke failures, unique-ref rules, demote rationale — keep short -->

…

## Done when

- [ ] Full inventory vs mapped include (or declared custom surface)
- [ ] Every row has workflow status
- [ ] Lifecycle + next action filled
- [ ] APPROVED / APPROVED (cimport) rows have decision-log evidence
- [ ] REJECTED rows have policy or measured why
- [ ] Present measuring: try-all **and** depth checklist in **this tracker’s** Experiment conclusions (**no skip**)
- [ ] **Bench results** table filled in **this file** (not only PR)
- [ ] **Before merge:** public PEP 257 one-liners in `cy{name}.pyi`; `.pxd` lean — [`PIPELINE.md`](../PIPELINE.md)
