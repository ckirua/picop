# Builtin method monkey-patches (archived — not in prod)

**Not shipped** in `src/cypy`. Do not restore into the package.

| | |
|--|--|
| **History** | Private predecessor [`cypy-private`](https://github.com/ckirua/cypy-private): branch [`cydict-monkey`](https://github.com/ckirua/cypy-private/tree/cydict-monkey) · PR [#7](https://github.com/ckirua/cypy-private/pull/7) |
| **Recipes** | [`archive/monkey-recipes`](https://github.com/ckirua/cypy-private/tree/archive/monkey-recipes/docs/future/monkey) on that private repo (C `ml_meth` swap, smoke, microbench) |

Pure-Python `dict.pop = …` fails on the immutable type; the archived recipe mutates `PyMethodDef.ml_meth` instead. Process-global, racy under free-threading, experiment-only — not a product API.
