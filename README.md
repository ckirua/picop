# picop

Fast CPython C-API helpers for Cython — typed hot-path wrappers plus C-backed UUID values.

**Python 3.15 is primary**, with Python 3.14 backward compatibility and genuine GIL-disabled support on **3.14t and 3.15t**. Minimum Python remains 3.14. Map of what is covered: [`COVERAGE.md`](COVERAGE.md). Primary license: [`LICENSE`](LICENSE) (MIT); adapted UUID portions retain their notices in [`NOTICE`](NOTICE) and [`LICENSES/Apache-2.0.txt`](LICENSES/Apache-2.0.txt). Contributing: [`CONTRIBUTING.md`](CONTRIBUTING.md). Security: [`SECURITY.md`](SECURITY.md). Safety / footguns: [`docs/SAFETY.md`](docs/SAFETY.md).

**Import:** use `picop` for both Python and Cython. The `cypy` Python imports and Cython cimport shims were removed in 3.0; migrate imports and cimports to the corresponding `picop` path.

## Migrating from 2.x

Replace the `cypy` prefix with `picop` in Python imports and Cython cimports:

```python
from picop.hot import bytes_len
from picop.uuid import UUID
```

```cython
from picop cimport UUID
from picop.uuid._uuid cimport UUID as DirectUUID, uuid_from_buf
```

Rebuild downstream Cython extensions against 3.0. Existing `picop` helper names
and signatures are unchanged; no `cypy` compatibility package or cimport shim
is shipped.

## Install
Commands below are run from the repository root unless noted; the repository root is the installable project.

PyPI distribution name and import package are both **`picop`**.

### From PyPI

```bash
pip install "picop==3.13.0"
```

Build deps (`setuptools`, `wheel`, `Cython>=3.3.0`, `picobuild`) are pulled via `pyproject.toml` `[build-system]`. Source installs need a C toolchain; UUID entropy uses the operating system (BCrypt on Windows, `/dev/urandom` elsewhere), with no third-party library linked. Compile extensions separately for each interpreter ABI; regular and free-threaded binaries are not interchangeable.

### From git (users)

```bash
pip install "picop @ git+https://github.com/ckirua/picop.git@picop-v3.13.0"
# or unpinned tip of main:
# pip install "picop @ git+https://github.com/ckirua/picop.git"
```

### Editable (contributors)

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

### Build artifacts

```bash
pip install build
python -m build          # sdist + wheel under dist/
# package_data ships .pxd / .pyi / py.typed / headers for cimport + typing
```

Prebuilt wheels are published with each release tag: cibuildwheel (config in
`pyproject.toml`, `[tool.cibuildwheel]`) builds manylinux, macOS universal2, and
Windows wheels for `cp314`/`cp315` and the free-threaded `cp314t`/`cp315t` tags, and
`publish.yml` uploads them alongside the sdist. `wheels.yml` runs the Linux x86_64
subset on every push to `main` and every pull request, so a broken extension build
fails before a release is cut.

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

Use only `picop` for Python imports and Cython cimports; there is no `cypy` compatibility shim in 3.0.

**Footgun:** C-string helpers take **`bytes`**, not `str`. Prefer `*_cstr` (`map_getitem_cstr`) — see `examples/py_cstr_bytes.py`. Broader trusted-caller notes (unchecked OOB, borrowed pointers, `marshal_loads`): [`docs/SAFETY.md`](docs/SAFETY.md).

For builtin or stdlib replacement candidates, use the
[consumer catalog](.cursor/skills/use-picop/catalog.md) and
[agent skill](.cursor/skills/use-picop/SKILL.md). The catalog records access
mode, semantic constraints, and available Python/Cython evidence; coverage is
not a speed guarantee. Profile the actual caller, prove equivalence, and retain
only repeatable improvements of at least 5% beyond measurement noise.

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

The C-backed `UUID` is a real final native subtype of `uuid.UUID`, accepts
32–36 UTF-8 bytes of hexadecimal text or exactly 16 bytes, and is immutable.
The integer slot is initialized eagerly; hash and stdlib descriptor access use valid inherited storage rather than a fabricated MRO. Integer construction fills Python's public `PyLongWriter` digit buffer directly on compatible native layouts, retaining the general byte conversion on other layouts. Cython callers can also use fixed-width checked integer conversions; see the [`cylong` tracker](docs/modules/021_cylong.md) and [Cython smoke demo](examples/cimport_ext/demo.pyx).
Generation uses per-thread buffered operating-system entropy with fork-child invalidation.
If the fork hook cannot be registered, import fails rather than allowing parent
and child to reuse buffered entropy. Custom `UUID_RANDOM_BUFFER_SIZE` builds
must use a positive multiple of 16 that fits the operating system entropy API's
length limit.
Float unpack wrappers validate input length before raw-pointer reads; see the trusted-caller [safety notes](docs/SAFETY.md). More Cython integer helper details are in the [`cylong` tracker](docs/modules/021_cylong.md) and [Cython smoke demo](examples/cimport_ext/demo.pyx).

Downstream Cython extensions **must rebuild** for this migration and for the UUID layout change. Use `from picop.uuid cimport …` or `from picop cimport …` for UUID typed factories; direct and barrel imports are supported. The old private UUID instance fields and binary layout are not retained.

## Examples

Runnable scripts after install — see [`examples/README.md`](examples/README.md):

```bash
python examples/pyhot.py
python examples/pybytes.py
python examples/pydict.py
```

## Compatibility

**1.0 policy:** **Core** (`picop.__all__` + `picop.hot`) and documented cimport contracts are frozen. Soft aliases were removed in **0.3**. Protocols / Runtime remain provisional under minors. See [`docs/RELEASE.md`](docs/RELEASE.md). Semantic twins like `dict_len`/`dict_size` stay dual (never identity-aliased). The 3.0 migration is complete; current stable is 3.13.0.

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
