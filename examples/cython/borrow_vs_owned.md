# Borrow vs owned (DX-05)

Public Python happy-path examples do not show ownership traps. Use this matrix when picking helpers:

| Need | Prefer | Avoid / note |
|------|--------|----------------|
| Dict get, miss and stored `None` both OK as `None` | `dict_get` | Cannot tell miss from `None` |
| Dict get, must see stored `None` | `dict_get_ref` | Strong ref |
| List get, index known in range | `list_get` | **No bounds check** (UB if OOB) |
| List get, may be OOB | `list_get_checked` / `list_get_ref` | Raises `IndexError` |
| Bytes as C `char*` in Cython | `bytes_as_string` (cimport) | Borrowed — do not mutate or outlive the `bytes` |

## Minimal Cython sketch

```cython
# cython: language_level=3
from picop.cydict cimport dict_get, dict_get_ref
from picop.cylist cimport list_get, list_get_checked

cdef object demo(dict d, list xs):
    # borrowed — None means miss OR stored None
    v = dict_get(d, "k")
    # owned / strong — can distinguish stored None
    v2 = dict_get_ref(d, "k")
    # unchecked index
    x0 = list_get(xs, 0)
    x1 = list_get_checked(xs, 1)
    return (v, v2, x0, x1)
```

Letter soft aliases (`dget`, `lget`, …) were removed in **0.3** — use preferred names.
