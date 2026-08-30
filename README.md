# picop

Fast CPython C-API helpers for Cython — typed hot-path wrappers plus C-backed UUID values.

Requires **Python ≥ 3.14**. Map of what is covered: [`COVERAGE.md`](COVERAGE.md). Primary license: [`LICENSE`](LICENSE) (MIT); adapted UUID portions retain their notices in [`NOTICE`](NOTICE) and [`LICENSES/Apache-2.0.txt`](LICENSES/Apache-2.0.txt). Contributing: [`CONTRIBUTING.md`](CONTRIBUTING.md). Security: [`SECURITY.md`](SECURITY.md). Safety / footguns: [`docs/SAFETY.md`](docs/SAFETY.md). Contributor process lives under [`docs/`](docs/) (not required for end users).

**Import rename (2.0):** prefer `import picop` / `from picop…`. The `cypy` import package is a **deprecated soft alias** (emits `DeprecationWarning`) and will be **removed in 3.0**. PyPI name was already `picop`.

## Install

PyPI distribution name and import package are both **`picop`**.

### From PyPI

```bash
pip install picop
# pin: pip install "picop==2.0.0"
```

Build deps (`setuptools`, `wheel`, `Cython`, `picobuild`) are pulled via `pyproject.toml` `[build-system]`. Source installs need a C toolchain and OpenSSL headers (`libssl-dev` on Debian/Ubuntu).

### From git (users)

```bash
pip install "picop @ git+https://github.com/ckirua/picop.git@v2.0.0"
# or unpinned tip of main:
# pip install "git+https://github.com/ckirua/picop.git"
```

### Editable (contributors)

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

### Build artifacts

```bash
pip install build
python -m build          # sdist + wheel under dist/
# package_data ships .pxd / .pyi / py.typed / headers for cimport + typing
```

Optional typecheck smoke (after install):

```bash
# requires pyright or mypy
pyright -c 'from picop.hot import dict_get, list_append'  # or:
python -c "from picop.hot import dict_get, list_len; reveal_type = print"  # stubs via py.typed
```

## Smoke

Prefer the curated starters module for micro-opts:

```python
from picop.hot import bytes_len, dict_get, list_len, str_len

assert bytes_len(b"ok") == 2
assert str_len("hi") == 2
assert dict_get({"a": 1}, "a") == 1
assert list_len([1, 2]) == 2
```

Also supported: `from picop.cydict import dict_get` / `from picop import dict_get`, and Cython `cimport`. Soft letter/bare aliases were removed in **0.3** — use preferred names. Prefer a release-tag pin. Avoid `from picop import *`.

Cython: both **`from picop cimport …`** (package barrel) and **`from picop.cybytes cimport …`** (submodule) work after install. Out-of-tree regression: [`examples/cimport_ext/`](examples/cimport_ext/) / `bash scripts/smoke_barrel_cimport.sh`.

Full public surface remains on `from picop import …` / `picop.cy*`. Deprecated: `from cypy…` / `from cypy… cimport` (soft alias until **3.0**).

**Footgun:** C-string helpers take **`bytes`**, not `str`. Prefer `*_cstr` (`map_getitem_cstr`) — see `examples/py_cstr_bytes.py`. Broader trusted-caller notes (unchecked OOB, borrowed pointers, `marshal_loads`): [`docs/SAFETY.md`](docs/SAFETY.md).

## UUID values

`picop.uuid` provides matching Python and Cython entry points:

```python
from picop.uuid import UUID, uuid4, uuid4_bytes

value = uuid4()
raw = uuid4_bytes()
assert UUID(raw).version == 4
```

```cython
from picop.uuid cimport UUID, uuid4, uuid4_bytes
```

The C-backed `UUID` is final, accepts 32–36 character hexadecimal text or
exactly 16 bytes, and remains a stdlib-compatible `uuid.UUID` value. Generation
uses per-thread buffered OpenSSL entropy with fork-child invalidation.

## Examples

Runnable scripts after install — see [`examples/README.md`](examples/README.md):

```bash
python examples/pyhot.py
python examples/pybytes.py
python examples/pydict.py
```

## Compatibility

**1.0 policy:** **Core** (`picop.__all__` + `picop.hot`) and documented cimport contracts are frozen. Soft aliases were removed in **0.3**. Protocols / Runtime remain provisional under minors. See [`docs/RELEASE.md`](docs/RELEASE.md). Semantic twins like `dict_len`/`dict_size` stay dual (never identity-aliased). Prefer pin: `pip install "picop==2.0.0"`.

**2.0 soft rename:** import package is **`picop`**; deprecated **`cypy`** alias remains until **3.0** (then removed). Pip install name was already `picop`.

Product tiers (Core / Protocols / Runtime): [`COVERAGE.md`](COVERAGE.md).

## Benchmarks

See [`bench/BENCH.md`](bench/BENCH.md). Quick Tier A run:

```bash
./bench/small.sh
```

## Docs

**User documentation:** [https://ckirua.github.io/picop/](https://ckirua.github.io/picop/) (Sphinx; sources under [`doc/`](doc/)). Local build: `pip install -e ".[docs]" --no-build-isolation` then `cd doc && make html`.

| Doc | Audience |
|-----|----------|
| [GitHub Pages site](https://ckirua.github.io/picop/) + [`doc/`](doc/) | External users (guides + API) |
| This README + [`examples/`](examples/) | External users (quick install / smoke) |
| [`COVERAGE.md`](COVERAGE.md) | What the library covers / does not (product map) |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Setup, checks, PR / freeze policy |
| [`SECURITY.md`](SECURITY.md) | Vulnerability reporting |
| [`docs/SAFETY.md`](docs/SAFETY.md) | Trusted-caller footguns |
| [`docs/`](docs/) | Contributor pipeline, status, module trackers |

Builtin monkey-patch experiments are **archived** under [`docs/future/MONKEY.md`](docs/future/MONKEY.md) and are **not** part of the package.
