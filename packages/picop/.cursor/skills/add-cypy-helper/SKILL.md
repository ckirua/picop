---
name: add-cypy-helper
description: >-
  Maintainer / post-1.0 Core freeze only. Implement or promote a cypy helper
  from a tracker TODO/ONGOING row on a per-module branch with PR
  (short/brief/detailed + benches). New modules or Core removals need major
  policy, not casual PRs. Never merge without user confirmation.
---

# Add or promote a cypy helper

**Audience:** maintainers after the **1.0 Core freeze**. Consumers should use `use-cypy`. New modules or Core removals need major policy — not casual PRs.
## When

User asks to implement a tracker TODO, promote a candidate, or add a `cy*` helper.

## Pipeline (required)

Follow [`docs/PIPELINE.md`](../../docs/PIPELINE.md):

1. Branch `mod/NN-cy{name}` (or continue that module’s open PR branch if already active).
2. Implement (steps below).
3. Run benches; update `docs/modules/NNN_cy{name}.md` (decision log + Bench results + Experiment conclusions).
4. Open or update PR with template sections + benchmark table. **Commit and push** when the improvement is done.
5. **Do not merge** until user confirms (push/PR updates OK).

## Implement steps

1. Read the module tracker (`docs/modules/NNN_cy{name}.md`) and `.cursor/rules/cypy-trackers.mdc`.
2. Implement in `src/cypy/cy{name}.pxd` (and `.pyx` if needed): typed args, no runtime type checks unless required.
3. **Docs:** public **PEP 257 one-liners** in `cy{name}.pyi`. Complete **depth** probes per [`docs/PIPELINE.md`](../../docs/PIPELINE.md) before APPROVED.
4. Export: public → `__init__.py` + `__all__` + `.pyi`; cimport-only → `cdef` + `__init__.pxd`.
5. Update tracker with Bench results **and** Experiment conclusions (why/scale/safety/ABI).
6. Examples smoke if public.
7. Prefer measuring + depth before final APPROVED.

## Do not

- Wrap entire C-API “for completeness”
- APPROVED without decision-log note
- Touch unrelated modules
- Merge without explicit user confirmation
