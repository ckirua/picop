# picop

Fast CPython C-API helpers for Cython — typed hot-path wrappers plus C-backed UUID values.

Requires **Python ≥ 3.14**. Prefer `import picop` (the deprecated `cypy` soft alias emits `DeprecationWarning` and will be removed in **3.0**).

```{toctree}
:maxdepth: 2
:hidden:

user_guide/install
user_guide/quickstart
user_guide/safety
user_guide/coverage
reference/index
whatsnew/index
```

## Start here

| Guide | What you get |
|-------|----------------|
| {doc}`user_guide/install` | PyPI, git, and editable installs |
| {doc}`user_guide/quickstart` | Smoke tests, `picop.hot`, Cython cimport |
| {doc}`user_guide/safety` | Trusted-caller footguns |
| {doc}`user_guide/coverage` | Core / Protocols / Runtime tiers |
| {doc}`reference/index` | Python API reference |
| {doc}`whatsnew/index` | Changelog |

```python
from picop.hot import bytes_len, dict_get, list_len, str_len

assert bytes_len(b"ok") == 2
assert str_len("hi") == 2
assert dict_get({"a": 1}, "a") == 1
assert list_len([1, 2]) == 2
```

Contributor process (pipeline, module trackers) lives under the repository `docs/` tree and is **not** part of this public site.
