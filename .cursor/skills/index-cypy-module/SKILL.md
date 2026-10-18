---
name: index-cypy-module
description: >-
  Maintainer / post-1.0 Core freeze only. Deep-index and depth-measure one
  cypy docs/modules/NNN_cy*.md tracker (full inventory, try-all candidates,
  why-win/lose probes, unique-ref/ABI/safety). Opens a per-module branch and
  PR; never merges without user confirmation. New modules or Core removals
  need major policy, not casual PRs.
---

# Index one cypy module (v2)

**Audience:** maintainers after the **1.0 Core freeze**. Consumers should use `use-cypy`. New modules or Core removals need major policy — not casual PRs.
## When

User asks to index / remake / upgrade a `docs/modules/NNN_cy*.md` tracker, or a named Order under `docs/modules/` (see [`docs/modules/README.md`](../../docs/modules/README.md); phase status lives in [`docs/README.md`](../../docs/README.md)).

## Pipeline (required)

Follow [`docs/PIPELINE.md`](../../docs/PIPELINE.md) end-to-end — especially **Measuring = try-all + depth**.

1. Branch `mod/NN-cy{name}`.
2. Index + measuring with **depth investigation** (not wrap-and-bench only).
3. Push + PR with benches **and** probe conclusions.
4. **Do not merge** until user confirms.

## Index steps

1. Identify module + Order (`NNN` from `docs/modules/NNN_cy{name}.md`).
2. Read TEMPLATE, exemplars (`cytuple`, `cybytes`), sources, Cython include.
3. Full v2 inventory — no skim.

## Measuring — try-all + depth

For **each** candidate: implement/smoke → bench → **depth probes** → decide.

Depth checklist (PIPELINE): why win/lose, scale/shape, semantics/safety, unique-ref/ownership, ABI/version, demotion rationale.  
**Also:** cheap sibling C-API aliases are compulsory (do not REJECT as “redundant” without wrapping).

**Forbidden:** APPROVED from a single toy-payload ratio when large/edge cases reverse the result (cybytes `bcontains` lesson).

## Before merge

PIPELINE checklist. **Must** refresh `docs/modules/NNN_cy{name}.md` (Bench results + Experiment conclusions) — **no skip**; PR-only evidence is invalid.

## Output

Branch + PR URL; **updated tracker** + QUEUE; waiting for merge confirmation.
