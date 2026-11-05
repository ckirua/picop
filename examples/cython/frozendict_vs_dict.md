# cyfrozendict — typed frozendict access in Cython

`frozendict` (CPython 3.15+) is **not** a `dict` subclass: `isinstance(fd, dict)`
is `False`, and the `dict_*` helpers in `picop.cydict` take a `PyDictObject`.
Guard before you touch the dict layout, and use `anydict_*` for the shared part.

```cython
from picop.cydict cimport dict_check, dict_get
from picop.cyfrozendict cimport (
    frozendict_check,
    frozendict_check_exact,
    anydict_check,
    anydict_check_exact,
    anydict_len,
    frozendict_new,
    frozendict_empty,
)

cdef object lookup(object d, object key):
    if dict_check(d):          # dict and dict subclasses only
        return dict_get(d, key)
    if frozendict_check(d):    # frozendict and frozendict subclasses
        return d[key]          # the read path is the same dict layout
    raise TypeError("expected a mapping")

cdef bint is_plain_dict(object d):
    return anydict_check_exact(d)   # dict or frozendict only — not defaultdict
```

## Copy semantics

`frozendict_new(fd)` returns **the same object** with an incremented reference:

```python
fd = frozendict({"a": 1})
assert frozendict_new(fd) is fd      # not a copy
```

Build from an iterable when you genuinely need a new object:
`frozendict_new(dict(fd))`.

## Python 3.14

Checks return `False`; `frozendict_new` / `frozendict_empty` raise
`NotImplementedError`. picop never substitutes a mutable `dict` for a frozen one,
so a `False` check on 3.14 means "no frozendict here", not "the type is missing
and a dict will do".
