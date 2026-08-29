# Install

PyPI distribution name and import package are both **`picop`**. Requires **Python ≥ 3.14**, a C toolchain for source builds, and OpenSSL headers (`libssl-dev` on Debian/Ubuntu) for UUID.

## From PyPI

```bash
pip install picop
# pin: pip install "picop==2.0.0"
```

Build deps (`setuptools`, `wheel`, `Cython`, `picobuild`) are pulled via `pyproject.toml` `[build-system]`.

## From git

```bash
pip install "picop @ git+https://github.com/ckirua/cypy.git@v2.0.0"
# or unpinned tip of main:
# pip install "git+https://github.com/ckirua/cypy.git"
```

## Editable (contributors)

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install setuptools wheel Cython picobuild
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
