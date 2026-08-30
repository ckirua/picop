# Quickstart

Prefer the curated starters module for micro-opts.

## Smoke

```python
from picop.hot import bytes_len, dict_get, list_len, str_len

assert bytes_len(b"ok") == 2
assert str_len("hi") == 2
assert dict_get({"a": 1}, "a") == 1
assert list_len([1, 2]) == 2
```

Also supported: `from picop.cydict import dict_get` / `from picop import dict_get`, and Cython `cimport`. Soft letter/bare aliases were removed in **0.3** — use preferred names. Prefer a release-tag pin. Avoid `from picop import *`.

**Import rename (2.0):** prefer `import picop`. The `cypy` import package is a **deprecated soft alias** (emits `DeprecationWarning`) and will be **removed in 3.0**.

## Hot starters

```python
from picop.hot import (
    dict_get, dict_len, dict_set, dict_contains, dict_pop, dict_setdefault,
    list_len, list_get, list_get_checked, list_append,
    set_contains, set_add,
    tuple_len, tuple_get, tuple_pack2,
    bytes_len, bytes_contains, bytes_eq,
    str_len, str_eq, str_contains,
    ansi_wrap, ansi_fg8, ansi_strip,
)

d = {"a": 1}
assert dict_get(d, "a") == 1 and dict_len(d) == 1

xs: list[object] = [1, 2]
assert list_len(xs) == 2 and list_get_checked(xs, 0) == 1
assert list_append(xs, 3) == 0  # 0 = success — not a boolean
```

## Cython cimport

Both **`from picop cimport …`** (package barrel) and **`from picop.cybytes cimport …`** (submodule) work after install:

```cython
from picop.cydict cimport dict_get, dict_len
from picop.cylist cimport list_len, list_get_checked
from picop.cybytes cimport bytes_len, bytes_contains, bytes_eq

cdef object hit(dict d, list xs, bytes b):
    return (
        dict_get(d, "k"),
        list_len(xs),
        list_get_checked(xs, 0),
        bytes_len(b),
        bytes_contains(b, b"a"),
        bytes_eq(b, b"a"),
    )
```

Out-of-tree regression: repository `examples/cimport_ext/` / `bash scripts/smoke_barrel_cimport.sh`.

Cimport-only / `cdef` symbols are **not** listed in the Python API reference — use them from Cython after install. Public Python / `cpdef` surface is what autodoc covers.

## UUID values

```python
from picop.uuid import UUID, uuid4, uuid4_bytes

value = uuid4()
raw = uuid4_bytes()
assert UUID(raw).version == 4
```

```cython
from picop.uuid cimport UUID, uuid4, uuid4_bytes
```

The C-backed `UUID` is final, accepts 32–36 character hexadecimal text or exactly 16 bytes, and remains a stdlib-compatible `uuid.UUID` value.

## Examples

Runnable scripts after install (repository `examples/`):

```bash
python examples/pyhot.py
python examples/pybytes.py
python examples/pydict.py
```

## Footgun

C-string helpers take **`bytes`**, not `str`. Prefer `*_cstr` (e.g. `map_getitem_cstr`) — see `examples/py_cstr_bytes.py`. Broader trusted-caller notes: {doc}`safety`.
