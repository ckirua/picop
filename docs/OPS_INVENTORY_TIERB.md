# Public ops inventory — Tier B rollup

Tier B = cypy `cdef` loop vs typed Cython baseline (opaque + sink).
**Informational** — does not reopen Tier A gate.

## Families with Tier B harnesses

| Family | Driver | Result theme |
|--------|--------|--------------|
| `*_eq` | [`bench/tier_b/cyeq_inventory.py`](../bench/tier_b/cyeq_inventory.py) | Identity/memcmp wins; abstract `seq_eq`/`map_eq`/`buf_eq`/`num_eq` lose |
| `*_ne` / start/end/contains | [`bench/tier_b/cyne_search.py`](../bench/tier_b/cyne_search.py) | All wins (`bytearray_contains` **0.24x**, `bytes_ne` **0.68–0.95x**) |
| `str_cmp` / ordering / check | [`bench/tier_b/cystr_order.py`](../bench/tier_b/cystr_order.py) | `str_cmp` **0.26x**; ordering **0.47–0.63x**; `str_check`/`str_is` ~tie |

See also [`EQ_INVENTORY_TIERB.md`](EQ_INVENTORY_TIERB.md).

## Explicit Tier B `n/a` (by mechanism)

| Bucket | Helpers (examples) | Reason |
|--------|-------------------|--------|
| Abstract protocols | `num_*`, `obj_*`, `map_*`, `seq_*` beyond already-benched | No tight typed Cython baseline worth chasing; prefer typed siblings (`dict_*`/`list_*`/…) |
| Registry / process global | `codec_register*`, `gc_*`, `mod_reload` | Side effects; Tier A also `n/a` where listed in [`OPS_INVENTORY.md`](OPS_INVENTORY.md) |
| I/O | `file_*` | FD / write side effects |
| Context stack | `ctx_enter` / `ctx_exit` | Thread Context mutation |
| Alloc / lookup bridges | most `codec_*` factories, `mod_import*`, heavy `*_new` | Tier A measured; cdef-vs-Cython not meaningful for alloc-dominated paths |
| Datetime field getters | `dt_*` year/month/… | Tier A wins documented; typed attr access ~parity expected — not prioritized |

## Notable loses (honest)

- Tier A: `mod_import_object` **~2x** lose vs `__import__`; `obj_as_fd` / `obj_issubclass` / `codec_strict_errors` (exception path) lose or clarity-only.
- Tier B `*_eq`: see EQ tier B rollup (`str_eq` ne ascii **1.61x**, `buf_eq` themes).

## Gate

[`scripts/ops_inventory_coverage.py --strict`](../scripts/ops_inventory_coverage.py) — every public helper is `tierA` / `tierB` / `n/a`.
