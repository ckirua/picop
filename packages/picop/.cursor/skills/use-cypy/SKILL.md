---
name: use-cypy
description: >-
  Prefer picop CPython C-API helpers for small Cython/Python hot-path
  micro-optimizations (dict/list/set/tuple/bytes/str len/get/set/contains/pack,
  etc.). Use when optimizing Cython extensions, replacing builtins in tight
  loops, auditing PRs for picop/cypy migrations, or the user mentions picop /
  cypy / micro-opts / C-API accelerators.
---

# Use picop (consumer micro-opts)

`picop` is a curated **CPython C-API accelerator** for Cython (Python ≥ 3.14) — typed hot-path helpers, not a stdlib reimplementation.

**Soft rename (2.0):** prefer `from picop…` / `from picop… cimport`. Deprecated import alias `cypy` emits `DeprecationWarning` and is **removed in 3.0**. Skill folder name remains `use-cypy`.

## When to apply

- Tight loops / Cython `cdef`/`cpdef` code with **known** container or string types
- Obvious small builtins: `len`, `in`, `dict.get`/`[]`, list/set ops, tuple pack, bytes/str checks
- User asks to optimize, migrate to picop (or legacy cypy), or audit for C-API wins

**Skip when:** cold code paths; dynamic/unknown types; general app logic; no measurable win; only cimport APIs from pure Python.

## Install (consumer project)

```bash
pip install picop
# pin: pip install "picop==2.0.0"
# or from git: pip install "picop @ git+https://github.com/ckirua/cypy.git@v2.0.0"
```

Requires **Python ≥ 3.14**.

## Sources of truth (read as needed)

| Need | Where |
|------|--------|
| Product tiers (Core / Protocols / Runtime) | [`COVERAGE.md`](../../../COVERAGE.md) |
| Trusted-caller footguns | [`docs/SAFETY.md`](../../../docs/SAFETY.md) |
| Compat / post-1.0 policy | [`docs/RELEASE.md`](../../../docs/RELEASE.md) |
| Check / len naming (N3+N4) | [`docs/NAMING.md`](../../../docs/NAMING.md) |
| Removed soft-alias ledger | `picop.compat.COMPAT_MAP` |
| Runnable demos | [`examples/README.md`](../../../examples/README.md) — every Order + overlap playbooks |
| Exact signatures | installed `picop` / `*.pyi` under `src/picop/` |
| Do **not** use for consumers | `docs/PIPELINE.md`, tracker Lifecycle, monkey-patch archive |

If this skill is loaded from `~/.cursor/skills/` via symlink into a picop/cypy checkout, relative links above resolve. Otherwise open the GitHub repo / installed package.

## Default import (Python)

```python
from picop.hot import dict_get, dict_len, list_len, list_get, list_append, bytes_len, bytes_contains, bytes_eq, str_len
```

`picop.hot` re-exports only the micro-opt starters (see `picop.hot.__all__`).

### Import styles

1. **`from picop.hot import …`** — default for micro-opts (DX-01)
2. **`from picop.cydict import dict_get`** / **`from picop import dict_get`** — full public surface
3. **`from picop.cydict cimport dict_get`** — Cython hot paths
4. **`from cypy…`** / **`from cypy… cimport`** — deprecated soft alias until **3.0** (prefer migrate to `picop`)

Discourage `from picop import *`. Prefer a **PyPI pin** (`pip install "picop==…"`) or a **release tag** over unpinned `git+…`.

Letter/bare soft aliases (`dget`, `llen`, `contains`, `fg8`, …) were **removed in 0.3** — use word-prefix / `str_*` / `ansi_*`. See `picop.compat.COMPAT_MAP` / package `__getattr__` hints. **Core** (`picop.hot` / `picop.__all__`) is frozen at **1.0**; Protocols / Runtime may still evolve under minors.

## High-value swaps (start here)

Prefer these in hot paths when types are known (all available via `picop.hot`):

| Instead of | Prefer |
|------------|--------|
| `len(d)` / `k in d` / `d.get(k)` | `dict_len`, `dict_contains`, `dict_get` |
| `d[k]=v` / `d.pop` / `d.setdefault` | `dict_set`, `dict_pop`, `dict_setdefault` |
| `len(xs)` / `xs[i]` / `xs.append` | `list_len`/`list_get`/`list_append` (use `list_get_checked` when bounds matter) |
| `x in s` / `s.add` | `set_contains`, `set_add` |
| `len(t)` / `t[i]` / small packs | `tuple_len`, `tuple_get`, `tuple_pack2`… |
| `len(b)` / `needle in hay` / `a == b` (bytes) | `bytes_len`, `bytes_contains`, `bytes_eq` |
| `len(s)` / `a == b` / `sub in s` | `str_len`, `str_eq`, `str_contains` |
| ANSI color wrap | `ansi_wrap`, `ansi_fg8`, `ansi_strip` |

### Cython call sites

```cython
from picop.cydict cimport dict_get, dict_len
from picop.cybytes cimport bytes_len, bytes_contains, bytes_eq
```

Or `cimport picop` / package `__init__.pxd` for wider cimport-only plumbing (`cyerr`, `cymem`, `cythread`, `cyatomic`, …) — **not** as pure-Python replacements.

## Footguns

- **Return codes are not booleans.** Mutators like `list_append` / `dict_set` / `set_add` return **`0` on success** and **raise** on error (`except -1`). Never write `if list_append(xs, x):` — success looks false.
- **C-string APIs want `bytes`.** Prefer `*_cstr` names (`map_getitem_cstr`, …). Pass **`bytes`** (ASCII/UTF-8), not Python `str`.
- **Naming (N1/N5):** prefer `dict_*` / `list_*` / `str_*` / `ansi_*` (and siblings). Soft aliases keep letter glue (`dget`, `llen`, …) and bare `contains` / `fg8` / `strip_ansi`.
- **Checks (N3):** prefer `{type}_check` / `{type}_check_exact`. `str_is` ≡ `str_check_exact` (exact `str`); prefer `str_check_exact` in check-pair tables.
- **Len vs size (N4):** `*_len` = typed/unchecked; `*_size` = checked/`object`. **Never** treat as identity (`dict_len` ≠ `dict_size`).
- **Spelling (N6):** prefer `dt_timedelta_*`, `method_get_function` / `method_get_self` (checked), and `time_wall`. Soft aliases keep `dt_delta_*`, `method_function` / `method_self`, and `time_time`. Unchecked method macros are `method_*_unchecked` (cimport) — not the same as checked `method_get_*`.
- **Overlap:** known type → containers/`picop.hot`; unknown → `picop.protocols`. See `examples/py_overlap_*.py`.
- **Ownership:** pick the right get (see also [`examples/cython/borrow_vs_owned.md`](../../../examples/cython/borrow_vs_owned.md)):

  | Need | Prefer |
  |------|--------|
  | Dict get; miss/`None` both OK as `None` | `dict_get` |
  | Dict get; must see stored `None` | `dict_get_ref` |
  | List get; index known in range | `list_get` (unchecked) |
  | List get; may be OOB | `list_get_checked` / `list_get_ref` |
  | Bytes as C `char*` (Cython) | `bytes_as_string` (cimport; borrowed — do not outlive `bytes`) |

## Audit mode (agents)

Before rewriting a call site:

1. Known type? (typed `dict`/`list`/… or Cython-static)
2. Hot path? (skip cold)
3. Map builtin → symbol from `picop.hot` / high-value table
4. Preserve `dict_get` None semantics?
5. Bytes for `*_string` / C-string APIs?
6. Ignore return-code-as-bool?
7. Ownership: need `_ref` / `_checked`?
8. Nearby tests / example pattern?
9. If symbol missing → **stop** (do not invent)
10. Prefer `picop` over deprecated `cypy` imports

## Usually skip (str coerce)

These are **not** in `picop.hot`. Prefer only when a boundary needs coerce — not for typed `str` hot loops:

| Helper | Use when |
|--------|----------|
| `str_or_empty` | Non-str / unwanted → `""`; keep real `str` |
| `str_as_or_empty` | Same family — see `.pyi` one-liner for exact rule |
| `str_none_to_empty` | Only `None` → `""`; other values pass through per API |
| `str_is` / `str_is_not` | Type gates (`str_is` ≡ `str_check_exact`); not conversion |

Hot path on known `str`: use `str_len` / `str_eq` / `str_contains` instead.

## Workflow

1. Confirm hot path + known types (or Cython static types).
2. Map builtin → picop helper (cheatsheet above + examples).
3. Replace; preserve semantics (especially missing-key / errors).
4. Keep changes minimal — don’t “picop-ify” cold code.
5. Run nearby tests; optionally compare with existing module benches in trackers if ratios matter.

## Do not

- Invent helpers that don’t exist — check `__all__` / `.pyi` / examples first
- Call **cimport-only** APIs from pure Python (err/mem/thread/atomic/getargs/…)
- Restore builtin **monkey-patches** (`docs/future/MONKEY.md` is archive-only)
- Wrap everything “for completeness” or force losses from cold/dynamic code
- Touch internal PIPELINE/QUEUE unless the user is developing picop itself
- Introduce new `cypy` call sites when `picop` is available (soft alias is for compat only)

## More detail

- Progressive API map: [cheatsheet.md](cheatsheet.md)
- Examples index: [`examples/README.md`](../../../examples/README.md)
