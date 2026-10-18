# picop

Fast CPython C-API helpers and C-backed UUID values for Cython.
CPython 3.15 is primary; 3.14, 3.14t and 3.15t remain supported.

The package lives in [`packages/picop`](packages/picop), which owns its build
metadata, tests, documentation and release lifecycle. The repository root is not
an installable Python distribution.

```bash
pip install ./packages/picop
```

## Agent guide

Repository-wide agent orientation and shared workflow rules: [`.agents/README.md`](.agents/README.md). Read it before the nearest package-local `AGENTS.md`; package-specific guidance remains authoritative for package changes.

Changes should remain within one package unless they intentionally update shared repository automation.
