# Pico packages

Monorepo for independently installable low-level Python packages.

| Package | Path | Purpose | Platform |
|---|---|---|---|
| `picop` | [`packages/picop`](packages/picop) | Main package: fast CPython C-API helpers and C-backed UUID values for Cython | CPython 3.15 primary; 3.14, 3.14t, 3.15t compatible |
| `picoipc` | [`packages/picoipc`](packages/picoipc) | Separate Linux shared-memory queue and local IPC primitives | Linux; CPython 3.14/3.15, regular and free-threaded |

`picop` is the primary package. `picoipc` remains an independent package for Linux IPC; install it separately when needed. Each package owns its build metadata, tests, documentation, and release lifecycle.

```bash
pip install ./packages/picop
pip install ./packages/picoipc
```


## Agent guide

Repository-wide agent orientation and shared workflow rules: [`.agents/README.md`](.agents/README.md). Read it before the nearest package-local `AGENTS.md`; package-specific guidance remains authoritative for package changes.

Changes should remain within one package unless they intentionally update shared repository automation.
