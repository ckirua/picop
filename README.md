# Pico packages

Monorepo for independently installable low-level Python packages.

| Package | Path | Purpose | Platform |
|---|---|---|---|
| `picop` | [`packages/picop`](packages/picop) | Fast CPython C-API helpers and C-backed UUID values for Cython | CPython 3.14+ |
| `picoipc` | [`packages/picoipc`](packages/picoipc) | Shared-memory queues and local IPC primitives | Linux, Python 3.14+ |

Each directory under `packages/` owns its build metadata, tests, documentation, and release lifecycle. Install a package from its directory rather than from the repository root:

```bash
pip install ./packages/picop
pip install ./packages/picoipc
```

Changes should remain within one package unless they intentionally update shared repository automation.
