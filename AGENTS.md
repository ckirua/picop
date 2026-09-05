# Agent guidance

This repository contains independently installable packages under `packages/`.

- Read and follow the nearest package-local `AGENTS.md` before changing a package.
- Keep package APIs, build metadata, tests, documentation, and release notes inside that package.
- Keep shared GitHub workflows under the repository-root `.github/workflows/` directory and scope them by package path.
- Do not introduce dependencies between packages unless the public product contract requires one.
- Run package commands from the relevant package directory; the repository root is not an installable Python distribution.
