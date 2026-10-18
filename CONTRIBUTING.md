# Contributing

Thanks for contributing to **picop** (repo / copyright: **ckirua**; historical import name `cypy`).

## Setup

Editable install (see root [`README.md`](README.md)):

```bash
python3.15 -m venv .venv
source .venv/bin/activate
pip install setuptools wheel 'Cython>=3.3.0' picobuild
pip install -e . --no-build-isolation
```

## Local checks

After changing public symbols or trackers:

```bash
# smoke
python -c "from picop.hot import bytes_len, dict_get, list_len, str_len"

# pytest (UUID + Core/hot/protocols/exports + example mains)
python -m pytest tests -q

# examples
for f in examples/py*.py examples/wrap_ansi.py; do python "$f"; done

# export / compat gate
python scripts/check_exports.py

# tracker grades (when docs/modules/ Lifecycle lines change)
python scripts/grade_trackers.py
```

Run installed-artifact correctness on 3.14, 3.15, 3.14t and 3.15t with separate
environments/builds. On t runtimes, first check `sys._is_gil_enabled()` before
and after importing `picop` with `PYTHON_GIL` unset; it must remain false. Run a
separate `python -X gil=0 -m pytest tests -q` concurrency suite. Do not reuse
native binaries between ABIs. Rebuild downstream Cython consumers using the
`picop` barrel and direct modules with
`PYTHON=/path/to/python bash scripts/smoke_barrel_cimport.sh`.

## Pull requests

Use [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md). Deep ship process (branch → measure → evidence → merge) lives in [`docs/PIPELINE.md`](docs/PIPELINE.md).

**Merge policy:** maintainers may auto-merge when the Before-merge checklist is green. External PRs need review before merge.

## 1.0 Core freeze

**Core** (`picop.__all__` + `picop.hot`) and documented cimport contracts are frozen at **1.0**:

- Additive minors are OK.
- Removals / semantic changes need a major.
- Soft aliases removed in **0.3** — **do not revive** them.

**3.0 release candidate:** use `picop` for Python imports and Cython cimports. The `cypy` package and cimport shims have been removed; no compatibility shim remains. Rebuild downstream Cython extensions after changing imports. `3.0.0rc1` is a prerelease.

Protocols / Runtime remain provisional under post-1.0 minor policy. See [`docs/RELEASE.md`](docs/RELEASE.md) and [`COVERAGE.md`](COVERAGE.md).

## Safety

Trusted-caller footguns (unchecked OOB, borrowed pointers, `marshal_loads`, `*_cstr` bytes): [`docs/SAFETY.md`](docs/SAFETY.md).
