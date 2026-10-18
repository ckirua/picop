# picop agent guide

Repository operating guide for coding agents and maintainers. Read this file first, then the package contract in [`AGENTS.md`](../AGENTS.md).

## Repository map

| Area | Purpose | Entry points |
|---|---|---|
| [`src/picop/`](../src/picop/) | CPython C-API helpers and C-backed UUID values for Cython | [`README.md`](../README.md), [`AGENTS.md`](../AGENTS.md), [`docs/`](../docs/) |
| [`src/cypy/`](../src/cypy/) | Deprecated import and cimport compatibility package | [`README.md`](../README.md#compatibility) |
| [`.github/workflows/`](../.github/workflows/) | picop CI, documentation and publishing | [`picop-smoke.yml`](../.github/workflows/picop-smoke.yml), [`publish.yml`](../.github/workflows/publish.yml) |

The repository root is the installable `picop` project. It owns the build metadata, tests, documentation and release notes. Run package commands here, including `pip install .`, `pip install -e .`, and `python -m build`.

## Working rules

1. Work from a dedicated branch based on current `main`; use a PR targeting `main`.
2. Follow the root `AGENTS.md` package contract.
3. Keep Python/Cython sources in `src/`, tests in `tests/`, and repository automation in `.github/workflows/`.
4. Run build, installation, test and release commands from the repository root.
5. Keep public-surface changes complete: callers, exports, stubs, tests, examples, package documentation, and release notes must agree.
6. Preserve the package contracts: picop Core is frozen and `cypy` remains a deprecated shim until 3.0.

## Package validation

Run the narrowest command that exercises the change, then the package gate when the change affects its contract or CI.

| Package | Required validation anchors |
|---|---|
| `picop` | `python scripts/check_exports.py`; relevant examples; use `bash scripts/smoke_barrel_cimport.sh` for cimport/package-artifact changes. |

## CI and release

- Keep workflows in [`.github/workflows/`](../.github/workflows/) with paths relative to the repository root.
- [`publish.yml`](../.github/workflows/publish.yml) publishes **picop only**, as an sdist, after a `picop-v*` tag or an explicit dispatch. Each publisher builds one Python 3.15 source archive, uploads it once, and requires independent installed-artifact validation on 3.14, 3.15, 3.14t and 3.15t before publication.
- Release PRs must pass picop's gate. Annotated `picop-vX.Y.Z` tags create a GitHub Release and publish through PyPI Trusted Publishing.
- A picop release requires a clean, current `main`, green CI, an explicit user-confirmed version and title, and the process in [`docs/RELEASE.md`](../docs/RELEASE.md). Preserve `picop`'s API/version policy and existing `scripts/release.sh` flow. Do not create tags or publish as part of ordinary maintenance work.
- [`.cursor/skills/`](../.cursor/skills/) contains the consumer, maintainer, and release skills. Refer to the relevant skill rather than duplicating a release process.

## Documentation ownership

Use this guide for repository orientation and keep product documentation in its existing locations:

- public Sphinx documentation: [`doc/`](../doc/)
- contributor and safety material: [`docs/`](../docs/)
- installation and API overview: [`README.md`](../README.md)

Update this file when the repository layout, CI or release process changes.
