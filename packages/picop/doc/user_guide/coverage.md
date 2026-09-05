# Coverage

Product contract for what `picop` is, what it ships, and how to choose helpers.

`picop` is **not** a reimplementation of the Python standard library, and it is **not** a full 1:1 port of Cython’s `Includes/cpython`. It is a curated **CPython C-API accelerator** for Cython on **Python ≥ 3.14**.

Prefer `picop`. Deprecated soft alias `cypy` (`DeprecationWarning`) until **3.0**, then removed.

## Product tiers

| Tier | Who | Import | Contents |
|------|-----|--------|----------|
| **Core** | Micro-opts / typed hot paths | `picop.hot` (preferred) or `from picop import …` | Typed containers, bytes/str, ANSI, GC toggles, string value ops |
| **Protocols** | Unknown concrete type | `picop` / `picop.cy*` | Abstract mapping/sequence/number/object bridges |
| **Runtime** | Extension / embedding authors | `picop` public + **cimport** SDK | datetime, codecs, marshal, file, weakref, capsule, contextvars, thin clocks, process plumbing |

**Rule of thumb:** prefer **Core** when the type is known; use **Protocols** only when it is not; use **Runtime** for non-hot-path / embedding needs.

### Core (prefer for micro-opts)

| Module | Maps to | Notes |
|--------|---------|--------|
| `cydict` | `dict` | `dict_get`, `dict_pop`, `dict_set`, `dict_len`, … |
| `cylist` | `list` | `list_append`, `list_get` / `list_get_checked`, `list_len`, … |
| `cytuple` | `tuple` | `tuple_get`, `tuple_len`, `tuple_pack*` |
| `cyset` | `set` / `frozenset` | `set_add`, `set_contains`, … |
| `cybytes` / `cybytearray` | `bytes` / `bytearray` | len / eq / contains / startswith / … |
| `cystr` / `cyunicode` | `str` value ops / UTF-8 intern | Prefer `cystr` for value ops |
| `cyansi` | terminal SGR | Not CPython; builds on unicode intern |
| `cygc` | GC | `gc_collect`, `gc_is_enabled`, … |
| `cyarray` / `cymemoryview` / `cybuffer` / `cyslice` | buffers / slice | Core-adjacent |

Curated starter export: {mod}`picop.hot`.

### 1.0 freeze (Core + cimport contracts)

As of **`1.0.0`**:

| Surface | Frozen? | Contract |
|---------|---------|----------|
| `picop.__all__` | **Yes** | Core star-import / discovery set — additive in minors; drop/rename/semantic change → major |
| `picop.hot.__all__` | **Yes** | Micro-opt marketing set — same policy |
| Full public barrel beyond `__all__` | Protocols/Runtime **provisional** | Still importable; may evolve under minors |
| `cimport picop` / `from picop.cy* cimport …` | **Documented SDK** | Wider than Python; cimport-only helpers stay out of this Python API reference |
| Soft letter/bare/`*_string` (post-0.3) | Implementation only | Prefer word-prefix / `*_cstr` |
| Deprecated `cypy` import / cimport | Soft alias | Prefer `picop`; **removed in 3.0** |

### Protocols (typed unknown)

| Module | Prefer instead when typed |
|--------|---------------------------|
| `cymapping` | `cydict` |
| `cysequence` | `cylist` / `cytuple` |
| `cynumber` | `cylong` / `cyfloat` / `cycomplex` / `cybool` |
| `cyobject` | typed module above |

### Runtime (public and/or cimport)

Public Runtime helpers include datetime, codecs, marshal, file, weakref, capsule, contextvars, `cytime` clocks, and object-model / scalar modules (`cyfunction`, `cymethod`, `cylong`, …). Embedding / process helpers such as `cyerr`, `cymem`, `cythread` are **cimport only** and are not documented here as Python callables.

## Import surfaces

| Entry | Role |
|-------|------|
| `from picop.hot import …` | **Core marketing surface** — micro-opt starters |
| `import picop` / `from picop import …` | Full public barrel; Core discovery via `__all__` |
| `from picop.cydict import dict_get` | Module-scoped public |
| `cimport picop` / `from picop.cydict cimport …` | **Full Cython SDK** (wider than Python) |
| `from cypy…` | **Deprecated** soft alias until **3.0** |

Discourage `from picop import *`.

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

## Not a goal

- Full Cython `cpython.*` parity or full Python stdlib
- Documenting every cimport / `cdef` symbol in the public Python API
- Treating Protocol/Runtime losers as Core micro-opt defaults
