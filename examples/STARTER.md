# Starter snippets (DX-07)

Copy-paste for the usual micro-opt path. Full demos: `pyhot.py`, `pydict.py`, `pylist.py`, `pybytes.py`, `pystr.py`, `pytuple.py`, `pyset.py`, `wrap_ansi.py`.

(`cypy` still works as a deprecated alias until 3.0.)

## Python

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

assert bytes_len(b"ok") == 2 and bytes_contains(b"ab", b"a")
assert bytes_eq(b"ok", b"ok")
assert str_len("hi") == 2 and str_contains("abc", "b")

# C-string helpers want bytes, not str — prefer *_cstr (see py_cstr_bytes.py)
from picop import map_getitem_cstr
assert map_getitem_cstr({"k": 1}, b"k") == 1
```

## Cython

```cython
from picop.cydict cimport dict_get, dict_len
from picop.cylist cimport list_len, list_get_checked
from picop.cybytes cimport bytes_len, bytes_contains, bytes_eq

cdef object hit(dict d, list xs, bytes b):
    return (dict_get(d, "k"), list_len(xs), list_get_checked(xs, 0), bytes_len(b), bytes_contains(b, b"a"), bytes_eq(b, b"a"))
```

Ownership matrix: [`cython/borrow_vs_owned.md`](cython/borrow_vs_owned.md).
