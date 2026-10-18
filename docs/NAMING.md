# Naming conventions (N3 + N4)

Rules for checks and length helpers. Enforced in skill / examples / `cypy.compat`;
export CI via [`scripts/check_exports.py`](../scripts/check_exports.py).

## N3 — `{type}_check` / `{type}_check_exact`

| Form | Meaning | C-API shape |
|------|---------|-------------|
| `{type}_check` | subtype OK (`isinstance`-like) | `Py*_Check` |
| `{type}_check_exact` | exact type only (`type is`) | `Py*_CheckExact` |

**Prefer** word-prefix pairs: `dict_check` / `dict_check_exact`, `list_check` / …,
`str_check` / `str_check_exact`, …

**Fold:** `str_is` is the same gate as `str_check_exact` (exact `str`). Prefer
`str_check_exact` in check-pair tables; `str_is` / `str_is_not` remain fine as
type-gate names in coerce docs. Soft letter forms (`dcheck`, `ucheck`, `is_str`)
were removed from the root barrel in **0.3**.

Specialized C-API names stay specialized (`set_any_check`, `weakref_check`,
`ctx_check_exact`, …) — do not invent missing subtype siblings.

## N4 — `*_len` (typed) vs `*_size` (checked)

| Form | When | Behavior |
|------|------|----------|
| `*_len(typed)` | Known exact type (`dict`, `list`, `bytes`, …) | Unchecked / macro path (`Py*_GET_SIZE`) |
| `*_size(object)` | Untyped / subtypes | Checked C-API (`Py*_Size`) |

**Never** identity-alias `*_len` to `*_size` — they are **semantic twins**
([`SEMANTIC_TWINS`](../src/cypy/compat.py)). Prefer `dict_len` on typed `dict`;
use `dict_size` when the object may be a subtype.

`obj_len` / `obj_size` are both checked length bridges (protocol/object tier);
prefer typed `*_len` when the concrete type is known.

## Soft aliases (Strategy B)

See [`COMPAT_MAP`](../src/cypy/compat.py): soft → preferred. Soft root names were
**removed in 0.3**; package `__getattr__` raises with `soft_alias_removal_hint`.
