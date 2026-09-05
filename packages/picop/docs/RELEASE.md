# Release checklist

Ship a tagged `picop` release from `main`. Version is sourced from [`src/picop/__about__.py`](../src/picop/__about__.py) (`pyproject.toml` dynamic version). The package lives at `packages/picop` in the `ckirua/picop` monorepo. Soft `cypy` import alias until **3.0**.

## Compatibility (0.x → 1.0)

**Locked policy (API refactor): Strategy B — soft then hard.**

| Change | Before 1.0 (0.x) | After 1.0 |
|--------|------------------|-----------|
| Add public symbol | OK | OK (minor) |
| Rename with dual alias | Preferred (`0.2` soft window) | Required ≥1 minor |
| Remove / rename without alias | OK if noted in tag notes | Forbidden without major |
| Change semantics of existing name | Avoid; new name instead | Major only |
| Promote cimport → public | OK | Minor |
| Demote public → cimport / drop from root | Soft-deprecate then remove in `0.3` | Major + long deprecation |
| Identity alias (`old is new`) | OK | OK during window |
| Semantic twin (`dlen` vs `dsize`) | **Keep both** — never alias as identity | Same |

**Version sketch:** `0.2` soft aliases + curated Core messaging → `0.3` hard trim of deprecated root names → `1.0` freeze **Core** public + documented cimport contracts. Protocols/Runtime may still evolve under minors after 1.0.

**Current (`1.0.0`+):** **Core** public (`picop.__all__` + `picop.hot`) and documented
cimport contracts are frozen. Soft root aliases were trimmed in `0.3`. Preferred
names only on `picop`; ledger + `__getattr__` hints: [`picop.compat`](../src/picop/compat.py).
Export gate: [`scripts/check_exports.py`](../scripts/check_exports.py).
Protocols / Runtime remain **provisional** under post-1.0 minor policy (see
[`CHANGELOG.md`](../CHANGELOG.md) / [`COVERAGE.md`](../COVERAGE.md)).

**2.0 soft import rename:** preferred import is **`picop`**. Deprecated **`cypy`** shim
(`DeprecationWarning` + cimport mirrors) until **3.0**, then removed. Pip name was
already `picop`.

**Alternative (not default):** Strategy A — single breaking `0.2` with **no** aliases (only if maintainers confirm near-zero external pins). Do not mix A and B halfway. **Chosen path was Strategy B** (soft then hard); do not reopen A for 1.x.

**Always:** update `use-cypy` skill, examples, and `__all__`/`.pyi` in the **same** rename wave; bare `cystr` names need extra care. Naming so far: **N2** `*_cstr`, **N6** spelling, **N1** word-prefix, **N5** `str_*`/`ansi_*`, **N3+N4** check/len conventions (docs + CI). Soft aliases **removed in 0.3**.

### 0.3 hard-trim checklist

1. [x] For each `COMPAT_MAP` soft name: drop root identity alias / dual import; update `.pxd` / `.pyi` duals.
2. [x] Short-lived `__getattr__` raises `AttributeError` with `soft_alias_removal_hint(name)`.
3. [x] Demote DEMOTE_ROOT soft-alias row (letter/bare/`*_string`/…); family demotions remain non-Core (not in `__all__`).
4. [x] Keep **semantic twins** (`*_len` / `*_size`).
5. [x] Bump to `0.3.0`; refresh skill pin + examples (preferred-only).
6. [x] Re-run `scripts/check_exports.py` + examples + grader (CI / local smoke).

### 1.0 Core freeze checklist

1. [x] Freeze Core public set (`picop.__all__` + `picop.hot`) and document cimport contracts in COVERAGE / module trackers.
2. [x] Changelog: close “Provisional (non-Core)” — Protocols/Runtime under post-1.0 minor policy.
3. [x] Tag `v1.0.0` (new monorepo releases use package-prefixed tags).

### 2.0 import rename checklist

1. [x] Tree under `src/picop/`; soft `src/cypy/` shim + `DeprecationWarning`.
2. [x] Cython cimport shims for `cypy` → `picop`.
3. [ ] **3.0:** remove `cypy` Python package and cimport shims; require `picop` only.

## Before tagging

| Step | Check |
|------|-------|
| 1 | On latest `main`; working tree clean |
| 2 | If any `docs/modules/` Lifecycle lines changed: `python scripts/grade_trackers.py` → **53/53 A** |
| 3 | Local smoke: `pip install -e . --no-build-isolation` then `from picop.hot import bytes_len, dict_get, str_len` |
| 4 | Examples: `for f in examples/py*.py examples/wrap_ansi.py; do python "$f"; done` |
| 5 | Export/compat: `python scripts/check_exports.py` |
| 6 | Confirm [`future/MONKEY.md`](future/MONKEY.md) is **not** wired into `src/picop` |
| 7 | Bump `__about__.__version__` (PEP 440), e.g. `2.0.0` |
| 8 | Update [`CHANGELOG.md`](../CHANGELOG.md) / [`README.md`](../README.md) status / [`COVERAGE.md`](../COVERAGE.md) if surface/policy changed |

## Tag and GitHub Release

Preferred: [`scripts/release.sh`](../scripts/release.sh)

```bash
# bump patch from __about__.py, commit, tag, GitHub Release, watch PyPI publish
scripts/release.sh --patch --title "short highlight"

# or explicit version
scripts/release.sh 2.0.0 --title "short highlight"

# preview only
scripts/release.sh --patch --dry-run
```

Manual equivalent:

```bash
git checkout main && git pull
# after version bump is on main:
git tag -a "picop-vX.Y.Z" -m "picop X.Y.Z"
git push origin "picop-vX.Y.Z"
gh release create "picop-vX.Y.Z" --title "picop X.Y.Z" --notes-file - <<'EOF'
## Highlights
- …

## Requires
- Python ≥ 3.14

## Install
```bash
pip install "picop==X.Y.Z"
# or: pip install "picop @ git+https://github.com/ckirua/picop.git@picop-vX.Y.Z#subdirectory=packages/picop"
```
EOF
```

Pushing the tag runs the repository-root [`.github/workflows/publish.yml`](../../../.github/workflows/publish.yml)
(Trusted Publishing → PyPI project **`picop`**, **sdist only**). Preferred import is **`picop`**;
deprecated **`cypy`** alias until **3.0**.
Plain `linux_*` wheels are rejected by PyPI; add manylinux via cibuildwheel later if needed.

### One-time PyPI Trusted Publisher

1. https://pypi.org/manage/account/publishing/ → pending publisher for **`picop`**
2. Owner `ckirua`, repo `picop`, workflow `publish.yml`, environment `pypi`
3. Optional: same on TestPyPI with environment `testpypi`
4. Create GitHub Environments `pypi` / `testpypi` (optional reviewers)

Manual dry-run: Actions → **publish** → Run workflow → `testpypi`.

## Artifacts / local PyPI check

```bash
pip install build twine
CPY_NATIVE=0 python -m build
twine check dist/*
# optional local upload (prefer CI Trusted Publishing):
# twine upload --repository testpypi dist/*
# twine upload dist/*
```

## Post-release verify

```bash
pip install "picop==X.Y.Z"
python -c "from picop.hot import bytes_len; assert bytes_len(b'ok') == 2"
```

Portable builds are the default (`-O3` only). Contributors may set `CPY_NATIVE=1` for local tuned benches — do **not** require it for release artifacts.
