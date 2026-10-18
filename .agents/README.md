# picop agent guide

Repository-wide operating guide for coding agents and maintainers. Read this file first, then the nearest [`AGENTS.md`](../AGENTS.md) for every package you change.

## Repository map

| Area | Purpose | Entry points |
|---|---|---|
| [`packages/picop/`](../packages/picop/) | CPython C-API helpers and C-backed UUID values for Cython | [`README.md`](../packages/picop/README.md), [`AGENTS.md`](../packages/picop/AGENTS.md), [`docs/`](../packages/picop/docs/) |
| [`.github/workflows/`](../.github/workflows/) | Path-scoped picop CI and publishing | [`picop-smoke.yml`](../.github/workflows/picop-smoke.yml), [`publish.yml`](../.github/workflows/publish.yml) |

The repository root is not an installable Python distribution. `packages/picop` owns the picop APIs, build metadata, tests, documentation and release notes.

## Working rules

1. Work from a dedicated branch based on current `main`; use a PR targeting `main`.
2. Read the closest package-local `AGENTS.md` before changing a package. Its package contract overrides this overview for package-specific work.
3. Keep product changes in `packages/picop`; use the repository root for shared automation and orientation.
4. Run package commands from that package directory. Do not use root-level installation as a substitute for package validation.
5. Keep public-surface changes complete: callers, exports, stubs, tests, examples, package documentation, and release notes must agree.
6. Preserve the package contracts: picop Core is frozen and `cypy` remains a deprecated shim until 3.0.

## Package validation

Run the narrowest command that exercises the change, then the package gate when the change affects its contract or CI.

| Package | Required validation anchors |
|---|---|
| `picop` | `python scripts/check_exports.py`; relevant examples; use `bash scripts/smoke_barrel_cimport.sh` for cimport/package-artifact changes. |

## Shared CI and release

- Keep shared workflows in [`.github/workflows/`](../.github/workflows/) and scope triggers by package path.
- [`publish.yml`](../.github/workflows/publish.yml) publishes **picop only**, as an sdist, after a `picop-v*` tag or an explicit dispatch. Each publisher builds one Python 3.15 source archive, uploads it once, and requires independent installed-artifact validation on 3.14, 3.15, 3.14t and 3.15t before publication.
- Release PRs must pass picop's gate. Annotated `picop-vX.Y.Z` tags create a GitHub Release and publish through PyPI Trusted Publishing.
- A picop release requires a clean, current `main`, green CI, an explicit user-confirmed version and title, and the process in [`packages/picop/docs/RELEASE.md`](../packages/picop/docs/RELEASE.md). Preserve `picop`'s API/version policy and existing `scripts/release.sh` flow. Do not create tags or publish as part of ordinary maintenance work.
- `packages/picop/.cursor/skills/` contains the picop consumer, maintainer, and release skills. Refer to the relevant skill rather than duplicating a release process.

## Documentation ownership

Use this guide for repository-level orientation only. Keep product documentation in its package:

- picop contributor and safety material: [`packages/picop/docs/`](../packages/picop/docs/)
- package installation and API documentation: [`packages/picop/README.md`](../packages/picop/README.md)

Update this file only when the repository layout, shared CI or release process changes.
