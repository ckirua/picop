# Pico agent guide

Repository-wide operating guide for coding agents and maintainers. Read this file first, then the nearest [`AGENTS.md`](../AGENTS.md) for every package you change.

## Repository map

| Area | Purpose | Entry points |
|---|---|---|
| [`packages/picop/`](../packages/picop/) | CPython C-API helpers and C-backed UUID values for Cython | [`README.md`](../packages/picop/README.md), [`AGENTS.md`](../packages/picop/AGENTS.md), [`docs/`](../packages/picop/docs/) |
| [`packages/picoipc/`](../packages/picoipc/) | Linux POSIX shared-memory SPSC ring and native bindings | [`README.md`](../packages/picoipc/README.md), [`AGENTS.md`](../packages/picoipc/AGENTS.md), [`research/`](../packages/picoipc/research/) |
| [`.github/workflows/`](../.github/workflows/) | Shared path-scoped CI and picop publishing | [`picop-smoke.yml`](../.github/workflows/picop-smoke.yml), [`picoipc-smoke.yml`](../.github/workflows/picoipc-smoke.yml), [`publish.yml`](../.github/workflows/publish.yml) |

The repository root is not an installable Python distribution. Packages are independently installable and own their APIs, build metadata, tests, documentation, and release notes.

## Working rules

1. Work from a dedicated branch based on current `main`; use a PR targeting `main`.
2. Read the closest package-local `AGENTS.md` before changing a package. Its package contract overrides this overview for package-specific work.
3. Keep a change inside one package unless it intentionally changes shared repository automation. Do not add package dependencies without a public-product requirement.
4. Run package commands from that package directory. Do not use root-level installation as a substitute for package validation.
5. Keep public-surface changes complete: callers, exports, stubs, tests, examples, package documentation, and release notes must agree.
6. Preserve the package contracts: `picop` Core is frozen and `cypy` remains a deprecated shim until 3.0; `picoipc` is Linux-only SPSC shared memory and must preserve its cross-backend wire layout.

## Package validation

Run the narrowest command that exercises the change, then the package gate when the change affects its contract or CI.

| Package | Required validation anchors |
|---|---|
| `picop` | `python scripts/check_exports.py`; relevant examples; use `bash scripts/smoke_barrel_cimport.sh` for cimport/package-artifact changes. |
| `picoipc` | `./bench/run_gate.sh` for the native correctness and production performance gate; run shared Ring tests with both `PICOIPC_BACKEND=pybind11` and `PICOIPC_BACKEND=pure` when changing portable Ring behavior. |

`picoipc`'s production benchmark comparison uses the committed pybind11 baseline. Do not refresh that baseline from ordinary CI or use a pure-Python result for the production comparison.

## Shared CI and release

- Keep shared workflows in [`.github/workflows/`](../.github/workflows/) and scope triggers by package path.
- [`publish.yml`](../.github/workflows/publish.yml) publishes **picop only**, as an sdist, after a `picop-v*` tag or an explicit dispatch. It validates the exact built sdist before artifact upload.
- A picop release requires a clean, current `main`, green CI, an explicit user-confirmed version and title, and the process in [`packages/picop/docs/RELEASE.md`](../packages/picop/docs/RELEASE.md). Do not create tags or publish as part of ordinary maintenance work.
- `packages/picop/.cursor/skills/` contains the picop consumer, maintainer, and release skills. Refer to the relevant skill rather than duplicating a release process.

## Documentation ownership

Use this guide for repository-level orientation only. Keep product documentation in its package:

- picop contributor and safety material: [`packages/picop/docs/`](../packages/picop/docs/)
- picoipc design, gate policy, and performance research: [`packages/picoipc/research/`](../packages/picoipc/research/)
- package installation and API documentation: each package's `README.md`

Update this file only when the repository layout, cross-package rules, shared CI, or global release process changes.
