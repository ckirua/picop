# Security

## Reporting

Please report vulnerabilities privately:

- GitHub **private vulnerability reporting** on [ckirua/picop](https://github.com/ckirua/picop), or
- Email: **aquipongoalgo.dsz@gmail.com**

Do not open a public issue for unfixed security bugs.

## Scope notes (trusted-caller APIs)

Several helpers are **trusted-caller footguns**, not remote RCE by themselves:

- **Unchecked OOB accessors** (`list_get`, `str_char_at`, and siblings) — out-of-bounds is undefined behavior; prefer `*_checked` or bounds you own.
- **`marshal_loads`** — untrusted data is unsafe (same class as stdlib `marshal.loads`).

Still report real package vulnerabilities (memory safety in checked paths, build/install issues that affect consumers, etc.).

More detail: [`docs/SAFETY.md`](docs/SAFETY.md).
