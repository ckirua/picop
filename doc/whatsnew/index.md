# What's new

Release history for `picop`. Prefer pinning a release tag for production.

```{toctree}
:maxdepth: 1

changelog
```

## Highlights

- **2.0.0** — import package renamed to `picop`; introduced the temporary `cypy` compatibility alias, later removed in 3.0.
- **3.0 (unreleased)** — remove `cypy` Python imports and Cython cimport shims; migrate to `picop` and rebuild downstream Cython extensions.
- **1.0.0** — Core (`picop.__all__` + `picop.hot`) and documented cimport contracts frozen.
