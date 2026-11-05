# Public ops inventory — Tier B rollup

Tier B = cypy `cdef` loop vs typed Cython baseline (opaque + sink).
**Informational** — does not reopen Tier A gate.

## Families with Tier B harnesses

| Family | Driver | Result theme |
|--------|--------|--------------|
| `*_eq` | [`bench/tier_b/cyeq_inventory.py`](../bench/tier_b/cyeq_inventory.py) | Identity/memcmp wins; abstract `seq_eq`/`map_eq`/`buf_eq`/`num_eq` lose |
| `*_ne` / start/end/contains | [`bench/tier_b/cyne_search.py`](../bench/tier_b/cyne_search.py) | All wins (`bytearray_contains` **0.24x**, `bytes_ne` **0.68–0.95x**) |
| `str_cmp` / ordering / check | [`bench/tier_b/cystr_order.py`](../bench/tier_b/cystr_order.py) | `str_cmp` **0.26x**; ordering **0.47–0.63x**; `str_check`/`str_is` ~tie |
| `call_*` / `call_method_*` | [`bench/tier_b/cycall.py`](../bench/tier_b/cycall.py) | `call_noargs` **0.97x**, `call_vector` NULL/pos+kw **0.93–0.98x**; method/arity variants **1.0–1.1x** (Cython already vectorcalls with a reserved slot) |
| `frozendict_*` / `anydict_*` | [`bench/tier_b/cyfrozendict.py`](../bench/tier_b/cyfrozendict.py) | `anydict_check_exact` **0.45–0.46x**, `anydict_len` **0.41–0.48x**, `_exact`/`anydict` checks **0.54–0.75x**; `frozendict_check` ties (Cython emits the same `PyObject_TypeCheck`) |
| `sentinel_check` / `sentinel_check_exact` | [`bench/tier_b/cysentinel.py`](../bench/tier_b/cysentinel.py) | Tier B checks 0.05–0.13x; compares against dynamically imported Python type-check logic, not an identical C macro baseline |
| `frame_*` | [`bench/tier_b/cyframe.py`](../bench/tier_b/cyframe.py) | `frame_check` 0.35–0.37x, `frame_lineno` 0.64–0.70x, `frame_code` 0.24–0.26x, `frame_back` 0.34x across default/depth passes |
| `code_*` | [`bench/tier_b/cycode.py`](../bench/tier_b/cycode.py) | `code_check` / `code_name` / `code_firstlineno` / `code_argcount` Tier B (0.14–0.37x); other public code readers Tier A |

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
