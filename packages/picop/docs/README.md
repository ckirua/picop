# cypy docs

> **Maintainer process.** Strangers should start at the root [`README.md`](../README.md), [`examples/`](../examples/), [`COVERAGE.md`](../COVERAGE.md), and [`SAFETY.md`](SAFETY.md) — not this folder’s pipeline / trackers.

## User vs process docs

| Audience | Start here | Do not need |
|----------|------------|-------------|
| **External users** (install & call helpers) | Root [`README.md`](../README.md), [`examples/`](../examples/), [`COVERAGE.md`](../COVERAGE.md), [`SAFETY.md`](SAFETY.md) | Tracker Lifecycle, PIPELINE stages |
| **Contributors** (ship / remaster modules) | This folder — especially [`PIPELINE.md`](PIPELINE.md) + [`modules/`](modules/) | — |

Process depth (trackers, Tier A/B benches, merge rules) stays under `docs/`. Product entry for strangers is the root README and examples.

## Status (complete — not an open backlog)

Phases 1–6 and the **1.0 Core freeze** are done. Per-module evidence lives in [`modules/`](modules/), not in Order tables here.

| Phase | Outcome |
|-------|---------|
| 1–2 | All 53 Orders indexed / decided |
| 3 | Depth remaster — **53/53 grade A** (`python scripts/grade_trackers.py`) |
| 4 | Tier B microbenches pasted / n/a |
| 5 | Git install + examples + release path |
| 6 | Usage examples for all Orders |
| API | Soft window `0.2` → hard trim `0.3` → Core freeze `1.0` |

Ship / remaster via [`PIPELINE.md`](PIPELINE.md) + [`TEMPLATE.md`](TEMPLATE.md). Product map: [`../COVERAGE.md`](../COVERAGE.md). Archive-only: [`future/MONKEY.md`](future/MONKEY.md) — do not restore into `src/cypy`.

## Doc map

| Path | Role |
|------|------|
| [`PIPELINE.md`](PIPELINE.md) | Full feature ship flow (branch → measure → PR) |
| [`NAMING.md`](NAMING.md) | N3/N4 check + len/size conventions |
| [`SAFETY.md`](SAFETY.md) | Trusted-caller footguns (OOB, borrow, marshal, `*_cstr`) |
| [`RELEASE.md`](RELEASE.md) | Version / tag / GitHub Release / PyPI (`picop`) checklist |
| [`../CHANGELOG.md`](../CHANGELOG.md) | Release notes; Core freeze at 1.0; Protocols/Runtime post-1.0 policy |
| [`TEMPLATE.md`](TEMPLATE.md) | v2 tracker template |
| [`modules/`](modules/) | **Trackers** — one `NNN_cy{name}.md` per module (Order `001`…`055`) |
| [`EQ_INVENTORY.md`](EQ_INVENTORY.md) · [`EQ_INVENTORY_TIERB.md`](EQ_INVENTORY_TIERB.md) · [`EQ_RUNTIME.md`](EQ_RUNTIME.md) · [`AGENT_LOOPS.md`](AGENT_LOOPS.md) | Grind `[eq/…]` issues via chat `/loop` or CLI agent in tmux |
| [`OPS_INVENTORY.md`](OPS_INVENTORY.md) · [`OPS_INVENTORY_TIERB.md`](OPS_INVENTORY_TIERB.md) | Full public-barrel ops checklist (Tier A/B / pending / n/a); gate: `scripts/ops_inventory_coverage.py` |
| [`future/MONKEY.md`](future/MONKEY.md) | Archived monkey-patch experiment — **not** in prod |

Bench harnesses: [`bench/BENCH.md`](../bench/BENCH.md). Coverage map: [`COVERAGE.md`](../COVERAGE.md). Grader: `python scripts/grade_trackers.py` (optional `--write-audit` regenerates a local depth audit).

## Status vocabularies (keep separate)

| Layer | Values | Meaning |
|-------|--------|---------|
| Module presence | `present` / `absent` | Has `src/cypy/cy*` or not |
| Tracker lifecycle | `stub` → `indexed` → `implementing` → `measuring` → `decided` | Process stage |
| Export | `public` / `cimport` / `cdef` / `—` | How a **cypy** symbol is exposed |
| Inventory layer | `cypy` / `C-API` / `used-by` | Helper vs raw symbol vs consumed |
| Workflow decision | `TODO` / `ONGOING` / `APPROVED` / `APPROVED (cimport)` / `REJECTED` | Keep public / keep Cython-only / drop |

Do **not** overload one “Status” column for all of the above.

## Bench gate (default)

| Tier | Baseline | When |
|------|----------|------|
| **A** | Plain Python | Public `cpdef` — `bench/cy*_bench.py` |
| **B** | Typed Cython `cdef` loop | Extension hot path — `bench/tier_b/` (informational; A gate unchanged) |

- **Primary metric:** mean wall time; **ratio = cypy / baseline**
- **APPROVED:** mean ratio ≤ **0.95** (≥5% win), or ≤ **1.02** + API-clarity note
- **APPROVED (cimport):** keep as `cdef` when useful but not public-worthy
- **REJECTED:** no keep rationale after try; log why in the tracker
- Paste timed tables + **depth** conclusions into **`docs/modules/NNN_cy{name}.md`** — **mandatory, no skip** (PR is not enough).  
Measuring = try-all **+** depth probes (see [`PIPELINE.md`](PIPELINE.md)).  
Before merge: public API docstrings in **`cy{name}.pyi`** — **PEP 257 one-liners**, no `Args:`/`Returns:`.

## Template checklist

Copy [`TEMPLATE.md`](TEMPLATE.md). Gold exemplar: [`modules/001_cytuple.md`](modules/001_cytuple.md).

1. Header · 2. Why · 3. Inventory (full) · 4. Workflow · 5. Lifecycle · 6. Decision log · 7. Bench notes · 8. Done when

## Module index

Trackers: [`modules/`](modules/) (present + absent). See that folder’s [`README.md`](modules/README.md) for the file list.
