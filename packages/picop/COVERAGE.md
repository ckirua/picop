# picop Coverage

Product contract for what `picop` is, what it ships, and how to choose helpers.

`picop` is **not** a reimplementation of the Python standard library, and it is **not** a full 1:1 port of Cython’s `Includes/cpython`. It is a curated **CPython C-API accelerator** for Cython on **Python ≥ 3.14**.

**Import (2.0):** prefer `picop`. Deprecated soft alias `cypy` (`DeprecationWarning`) until **3.0**, then removed. Pip name is already `picop`.

Authoritative symbol lists: `src/picop/__init__.py` / `__init__.pxd` `__all__`, plus `picop.hot` for micro-opt starters. Per-module decisions: [`docs/modules/`](docs/modules/).
Timed public-ops checklist: [`docs/OPS_INVENTORY.md`](docs/OPS_INVENTORY.md) (gate: `scripts/ops_inventory_coverage.py --strict`).

---

## Product tiers

| Tier | Who | Import | Contents |
|------|-----|--------|----------|
| **Core** | Micro-opts / typed hot paths | `picop.hot` (preferred) or `from picop import …` | Typed containers, bytes/str, ANSI, GC toggles, string value ops |
| **Protocols** | Unknown concrete type | `picop` / `picop.cy*` | Abstract mapping/sequence/number/object bridges |
| **Runtime** | Extension / embedding authors | `picop` public + **cimport** SDK | datetime, codecs, marshal, file, weakref, capsule, contextvars, thin clocks, process plumbing |

**Rule of thumb:** prefer **Core** when the type is known; use **Protocols** only when it is not; use **Runtime** for non-hot-path / embedding needs.

### Core (prefer for micro-opts)

| Module | Maps to | Surface | Notes |
|--------|---------|---------|--------|
| `cydict` | `dict` | public + cimport | `dict_get`, `dict_pop`, `dict_set`, `dict_len`, `dict_eq`, … |
| `cydeque` | `collections.deque` | public | `deque_eq` |
| `cyrange` | `range` | public | `range_eq` |
| `cylist` | `list` | public + cimport | `list_append`, `list_get` / `list_get_checked`, `list_len`, `list_eq`, … |
| `cyset` | `set` / `frozenset` | public + cimport | `set_add`, `set_contains`, `set_eq`, `frozenset_eq`, … |
| `cytuple` | `tuple` | public + cimport | `tuple_get`, `tuple_len`, `tuple_pack*`; builders mostly cimport |
| `cybytes` | `bytes` | public + cimport | `bytes_len`, `bytes_contains`, `bytes_eq`, `bytes_ne`, `bytes_startswith`, `bytes_endswith`, `bytes_bytearray_eq`; `bytes_as_string` cimport-only |
| `cybytearray` | `bytearray` | public + cimport | `bytearray_len`, `bytearray_eq`, `bytearray_ne`, `bytearray_contains`, `bytearray_from_object`, … |
| `cystr` | `str` value ops | public subset + cimport | `str_len`, `str_eq`, `str_cmp`, `str_lt`/`le`/`gt`/`ge`, `str_contains`, coerce helpers, … |
| `cyunicode` | UTF-8 / intern | public subset + cimport | `uintern`, `uutf8_bytes`; `unicode_from_string` / `uutf8` cimport |
| `cyansi` | terminal SGR | public | Not CPython; builds on unicode intern |
| `cygc` | GC | public | `gc_collect`, `gc_is_enabled`, … |
| `cyarray` / `cymemoryview` / `cybuffer` / `cyslice` | buffers / slice | public | `array_eq` / `array_ne`; `memoryview_eq` / `memoryview_ne`; `buf_eq`; `slice_eq`; sequences/buffers adjacent to Core |

**Curated starter export:** [`picop.hot`](src/picop/hot.py) — see [`examples/STARTER.md`](examples/STARTER.md).

### 1.0 freeze (Core + cimport contracts)

As of **`1.0.0`**:

| Surface | Frozen? | Contract |
|---------|---------|----------|
| `picop.__all__` | **Yes** | Core star-import / discovery set — additive in minors; drop/rename/semantic change → major |
| `picop.hot.__all__` | **Yes** | Micro-opt marketing set — same policy |
| Full public barrel (`from picop import name` beyond `__all__`) | Protocols/Runtime **provisional** | Still importable; may evolve under minors (see CHANGELOG) |
| `cimport picop` / `from picop.cy* cimport …` | **Documented SDK** | Wider than Python; per-module **Surface** + inventory in [`docs/modules/`](docs/modules/) are authoritative |
| Core names that are also `cpdef`/`cdef` | **Yes** | Same symbol, same semantics as public Core |
| `cdef`-only helpers (builders, unique-ref fill, C-string keys, borrow pointers, …) | **Documented cimport** | Keep for Cython; never promote to pure-Python without a minor; demote/remove → major after advertise |
| Soft letter/bare/`*_string` (post-0.3) | Implementation only | Not a public or cimport *product* contract; prefer word-prefix / `*_cstr` |
| Deprecated `cypy` import / cimport (2.0 soft window) | Soft alias | Prefer `picop`; **removed in 3.0** |

**Authoritative lists:** `src/picop/__init__.py` / `hot.py` `__all__`, `src/picop/__init__.pxd` + `cy*.pxd`, tracker inventories.

### Protocols (typed unknown)

| Module | Prefer instead when typed | Notes |
|--------|---------------------------|--------|
| `cymapping` | `cydict` | `map_*` / `map_eq` — checks often win; prefer typed `dict_eq` |
| `cysequence` | `cylist` / `cytuple` | `sq*` / `seq_eq` — prefer typed `list_eq`/`tuple_eq` |
| `cynumber` | `cylong` / `cyfloat` / `cycomplex` / `cybool` | Binary ops often lose; prefer typed `long_eq` / `float_eq` / `complex_eq` / `bool_eq` when known; `num_eq` for protocol bridges |
| `cyobject` | typed module above | Last resort attr/item/call bridges; `obj_eq` via RichCompareBool (not `hot`) |

### Runtime (public and/or cimport)

| Module | Surface | Notes |
|--------|---------|--------|
| `cydatetime`, `cycodecs`, `cymarshal`, `cyfileobject`, `cyweakref`, `cypycapsule`, `cycontextvars` | public (+ some cimport) | Higher-level C-API bridges; `dt_*_eq` / `capsule_eq` / `weakref_eq` / `context_eq` on `picop` (not `hot`); see `docs/EQ_RUNTIME.md` |
| `cytime` | public | Thin `time_wall` / `time_time` / `time_monotonic` / `time_perf_counter` — **Runtime**, not Core (`picop.hot` excludes them). Prefer stdlib `time` unless you need these wrappers; prefer `time_wall` over stutter `time_time`. |
| `cyfunction`, `cymethod`, `cymodule`, `cyiterator`, `cyiterobject`, `cygenobject`, `cycellobject`, `cydescr`, `cytype`, `cylong`, `cyfloat`, … | public | Object-model / scalar helpers; `func_eq` / `method_eq` / `mod_eq` / `gen_eq` / `iter_eq` / `type_eq` identity-or-richcompare / `cell_eq` content (not `hot`) |
| `cyerr`, `cymem`, `cythread`, `cyatomic`, `cyref`, `cygetargs`, `cyceval`, `cypystate`, `cypylifecycle`, `cypyport`, `cyversion`, `cylongintrepr` | **cimport only** | Embedding / process footguns — not pure-Python |
| `cyinstance` | **none** | Classic-class ABI gone on 3.14 |

---

## Import surfaces

| Entry | Role |
|-------|------|
| `from picop.hot import …` | **Core marketing surface** — micro-opt starters |
| `import picop` / `from picop import …` | Full public barrel; Core discovery via `__all__` (frozen at 1.0) |
| `from picop.cydict import dict_get` | Module-scoped public |
| `cimport picop` / `from picop.cydict cimport …` | **Full Cython SDK** (wider than Python; includes cimport-only) |
| `from cypy…` / `from cypy… cimport` | **Deprecated** soft alias (2.0); emits `DeprecationWarning`; **removed in 3.0** |

Discourage `from picop import *`.

---

## Overlap decision tree

```
Known concrete type?
  dict  → cydict (dict_get, dict_len, …)
  list  → cylist
  tuple → cytuple
  set   → cyset
  bytes → cybytes
  str   → cystr value ops; encode/intern → cyunicode
Unknown mapping / sequence / number-like?
  → cymapping / cysequence / cynumber
Still too dynamic?
  → cyobject (last resort)
```

**Do not merge modules** (C-API includes differ). Trackers already say “prefer typed when known.”

**Playbook examples:** [`py_overlap_mapping_vs_dict.py`](examples/py_overlap_mapping_vs_dict.py),
[`py_overlap_sequence_vs_list.py`](examples/py_overlap_sequence_vs_list.py),
[`py_overlap_str_vs_unicode.py`](examples/py_overlap_str_vs_unicode.py).

### String family (two layers, one product)

| Layer | Module | Role |
|-------|--------|------|
| Value ops on `str` | `cystr` | len/eq/contains/concat/coerce/… |
| Encode / intern / borrow | `cyunicode` | `uintern`, `uutf8_bytes`, cimport `unicode_from_string` / `uutf8` |

### Naming conventions (N3 + N4)

| Rule | Prefer | Notes |
|------|--------|-------|
| Checks | `{type}_check` / `{type}_check_exact` | Subtype vs exact; `str_is` ≡ `str_check_exact` |
| Length | `*_len(typed)` vs `*_size(object)` | Macro/unchecked vs checked — **semantic twins**, never identity |

Full table: [`docs/NAMING.md`](docs/NAMING.md). Removed soft aliases (0.3+): [`picop.compat.COMPAT_MAP`](src/picop/compat.py).

### Category facades (optional discovery)

| Import | Contents |
|--------|----------|
| `picop.hot` | Micro-opt starters (preferred; **Core frozen**) |
| `picop.containers` | dict / list / set / tuple (Core-adjacent) |
| `picop.buffers` | bytes / bytearray / array / memoryview / buffer / slice |
| `picop.protocols` | mapping / sequence / number / object — **provisional** after 1.0 |

---

## Layers (implementation)

| Layer | Entry | Role |
|-------|-------|------|
| Public Python | `__init__.py`, `hot.py` | Callable helpers |
| Cython cimport | `__init__.pxd`, `cy*.pxd` | Wider SDK |
| Implementation | `cy*.pxd` (+ `.pyx`) | Inline C-API wrappers |

---

## Not a goal

- Full Cython `cpython.*` parity or full Python stdlib (`json`, `os`, `re`, `asyncio`, …)
- Restoring builtin monkey-patches ([`docs/future/MONKEY.md`](docs/future/MONKEY.md))
- Treating Protocol/Runtime losers as Core micro-opt defaults

Historical note: an older tree lived as `cycel.core.cpy`. **`cytime` ships in picop as Runtime** (not deferred to `cycel.time`). Broader clock/RFC utilities may still live in sibling packages. Pre-2.0 import name was `cypy` (soft alias until 3.0).

---

## Related

- Install / smoke: [`README.md`](README.md)
- Safety / footguns: [`docs/SAFETY.md`](docs/SAFETY.md)
- Naming: [`docs/NAMING.md`](docs/NAMING.md)
- Compatibility / release: [`docs/RELEASE.md`](docs/RELEASE.md)
- Trackers: [`docs/modules/`](docs/modules/) · Status (complete): [`docs/README.md`](docs/README.md#status-complete--not-an-open-backlog)
