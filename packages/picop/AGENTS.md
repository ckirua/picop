# Agent guidance (picop / cypy)

Rules for coding agents working in this repo or consuming the package.

## Prefer `picop.hot`

For micro-opts, default to `from picop.hot import …`. Full public surface remains on `from picop import …` / `picop.cy*`. Soft letter/bare aliases were removed in **0.3** — never revive them.

**Soft rename (2.0 → 3.0):** `cypy` is a deprecated import alias (`DeprecationWarning`); prefer `picop`. The `cypy` package and cimport shims are removed in **3.0**. Skill folder name stays `use-cypy`.

## Keep surface consistent

When adding or renaming a public helper, update in the **same** change:

- `picop.__all__` / module exports
- `.pyi` stubs (PEP 257 one-liners)
- examples (as needed)
- [`CHANGELOG.md`](CHANGELOG.md)

Run `python scripts/check_exports.py` and the relevant examples.

## Core freeze

**Core** (`picop.__all__` + `picop.hot`) is frozen at **1.0**. Additive minors OK; no soft-alias revivals; removals need a major. See [`docs/RELEASE.md`](docs/RELEASE.md).

## Maintainer skills vs consumers

| Skill | Role |
|-------|------|
| [`.cursor/skills/use-cypy/SKILL.md`](.cursor/skills/use-cypy/SKILL.md) | **Consumer** guidance — prefer this for call-site migrations |
| `add-cypy-helper` / `index-cypy-module` | **Maintainer / post-1.0 Core freeze** — tracker work only; new modules or Core removals need major policy, not casual PRs |
| [`.cursor/skills/release-picop/SKILL.md`](.cursor/skills/release-picop/SKILL.md) | **Maintainer release** — tag / PyPI publish via `scripts/release.sh` (confirm with user; `@`-mention skill) |

## Safety

Read [`docs/SAFETY.md`](docs/SAFETY.md) before wrapping unchecked / borrowed / marshal APIs.

## Eq-issue loops

To iterate open `[eq/…]` enhancements (`/loop` in chat or headless CLI in tmux), see [`docs/AGENT_LOOPS.md`](docs/AGENT_LOOPS.md).
