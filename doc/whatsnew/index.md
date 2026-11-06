# What's new

Release history for `picop`. Prefer pinning a release tag for production.

```{toctree}
:maxdepth: 1

changelog
```

## Highlights

- **3.3.0** — `cylock` cimport-only `PyMutex` helpers for free-threaded extensions, plus `docs/PERF_PARITY.md` and "slower than the builtin" notes on every Tier-A-losing stub.
- **3.2.0** — `cyframe`, `cycode`, and `cytraceback` accessor suites with refcount-balanced getters; `cycellobject` cell-borrow fix.
- **3.1.0** — CPython 3.15 `cysentinel` and `cyfrozendict` surfaces; `cycall` vectorcall helpers (bound-method helpers cimport-only).
- **3.0.0** — remove `cypy` Python imports and Cython cimport shims; migrate to `picop` and rebuild downstream Cython extensions. Retain Python 3.14/3.15 and genuine GIL-disabled 3.14t/3.15t support.
- **2.0.0** — import package renamed to `picop`; introduced the temporary `cypy` compatibility alias, later removed in 3.0.
- **1.0.0** — Core (`picop.__all__` + `picop.hot`) and documented cimport contracts frozen.
