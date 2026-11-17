# Install

Requires **Python ≥ 3.14**, with a C toolchain for source builds. UUID entropy
uses the operating system (BCrypt on Windows, `/dev/urandom` elsewhere); no
third-party library is linked.

Python **3.15 is primary**; 3.14, 3.14t and 3.15t are also supported. Imports on
free-threaded interpreters do not enable the GIL. Each ABI needs its own
extension build, and downstream Cython extensions must rebuild for the UUID
layout change.

## From PyPI

```bash
pip install "picop==3.13.0"
```

The `cypy` import and cimport namespace were removed in 3.0; migrate callers
to `picop` and rebuild downstream Cython extensions.

Build deps (`setuptools`, `wheel`, `Cython>=3.3.0`, `picobuild`) are pulled via `pyproject.toml` `[build-system]`.

## From git

```bash
pip install "picop @ git+https://github.com/ckirua/picop.git@picop-v3.13.0"
# or unpinned tip of main:
# pip install "picop @ git+https://github.com/ckirua/picop.git"
```

## Editable (contributors)

```bash
python3.15 -m venv .venv
source .venv/bin/activate
pip install setuptools wheel 'Cython>=3.3.0' picobuild
pip install -e . --no-build-isolation
```

Release builds are **portable** by default (`-O3` only). For local microbenches that want CPU-tuned code:

```bash
CPY_NATIVE=1 pip install -e . --no-build-isolation
```

## Build artifacts

```bash
pip install build
python -m build          # sdist + wheel under dist/
# package_data ships .pxd / .pyi / py.typed / headers for cimport + typing
```

Optional typecheck smoke (after install):

```bash
# requires pyright or mypy
pyright -c 'from picop.hot import dict_get, list_append'
```

## Documentation build (optional)

```bash
pip install -e ".[docs]" --no-build-isolation
cd doc && make html
# open _build/html/index.html
```
