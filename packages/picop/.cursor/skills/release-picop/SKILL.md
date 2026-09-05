---
name: release-picop
description: >-
  Tag and publish the picop package (PyPI dist picop) via
  scripts/release.sh, Trusted Publishing, and picop-v* tags. Use when the user
  asks to release, tag, publish to PyPI, bump version, or ship a picop release.
  @-mention this skill for release work; do not invent a release path.
disable-model-invocation: true
---

# Release picop

**Audience:** maintainers shipping a tagged **`picop`** release. Consumers use `use-cypy`. Policy and checklists live in [`docs/RELEASE.md`](../../../docs/RELEASE.md).

## When

User asks to **release**, **tag**, **publish** (PyPI), or **bump version** for picop/cypy.

## Product names

| Role | Name |
|------|------|
| PyPI / pip | **`picop`** |
| Preferred import | **`picop`** (`from picop.hot import …`) |
| Deprecated import | **`cypy`** until **3.0** |
| GitHub monorepo | `ckirua/picop` (`packages/picop`) |
| Version source | `src/picop/__about__.py` (prefer this; legacy trees may still use `src/cypy/__about__.py`) |

## Preconditions

- On **`main`**, clean tree, synced with `origin/main`
- Version bump / release commit intended for main (if shipping from a PR: merge first, CI green)
- Confirm **version** and release **title** with the user before any non-`--dry-run` run

## Preferred path

[`scripts/release.sh`](../../../scripts/release.sh) bumps `__about__`, updates `CHANGELOG.md` / install pins, commits, pushes `main`, creates an annotated `picop-vX.Y.Z` tag and GitHub Release, and watches the repository-root `publish.yml` workflow.

```bash
scripts/release.sh --patch --title "short highlight"
scripts/release.sh 2.0.1 --title "short highlight"
scripts/release.sh --patch --dry-run   # preview first
```

Also: `--minor` / `--major`, `--notes-file`, `--no-push` (commit only). Prefer dry-run before the real cut.

## Manual fallback

Only if the script cannot run. See **Tag and GitHub Release** in [`docs/RELEASE.md`](../../../docs/RELEASE.md): bump version on main → `git tag -a picop-vX.Y.Z` → `git push origin picop-vX.Y.Z` → `gh release create …`. Pushing `picop-v*` triggers publish.

## PyPI

- **Trusted Publishing (OIDC)** uses workflow `publish.yml` and environment `pypi`
- **sdist only** — plain `linux_*` wheels are rejected; manylinux is a later follow-up
- Tag push publishes to PyPI; `workflow_dispatch` can target TestPyPI

## Versioning (pointer)

Full policy: [`docs/RELEASE.md`](../../../docs/RELEASE.md).

- **Core** (`picop.__all__` + `picop.hot`) frozen at **1.0** — additive minors OK; removals / breaking need a **major**
- Soft import rename: prefer **`picop`** in **2.x**; remove **`cypy`** in **3.0**
- Do not reopen Strategy A for 1.x

## Agent safety

- **Confirm version + title** with the user before running without `--dry-run`
- **Do not** push tags or cut a release unless the user explicitly asked to release
- **Never** force-push tags; **never** skip hooks (`--no-verify` / release `--skip-checks` only if user insists)
- **Never** merge or tag without user confirmation when an agent is shipping
- After publish: `pip install "picop==X.Y.Z"` then `from picop.hot import bytes_len`

## Do not

- Duplicate the full RELEASE checklist here — read the doc when details matter
- Upload with twine tokens when CI Trusted Publishing is available
- Require `CPY_NATIVE=1` for release artifacts
