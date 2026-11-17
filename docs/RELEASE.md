# Release checklist

Release and validation commands below are run from the repository root unless noted.

Ship a tagged `picop` release from `main`. Version is sourced from [`src/picop/__about__.py`](../src/picop/__about__.py) (`pyproject.toml` dynamic version). The repository root is the installable `picop` project. 3.0 removes the former `cypy` Python import and Cython cimport shims.

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

**Current policy:** **Core** public (`picop.__all__` + `picop.hot`) and documented
cimport contracts are frozen. Removals/semantic breaks require a major; additive
public APIs follow the policy above. Protocols / Runtime remain **provisional**
under post-1.0 minor policy (see [`CHANGELOG.md`](../CHANGELOG.md) / [`COVERAGE.md`](../COVERAGE.md)).

Major-version readiness is a compatibility decision, not an automatic release
gate: identify the intended breaking changes, audit affected public and
documented cimport contracts and migration needs, update changelog/docs/tests,
and validate the supported runtimes and release artifacts. The release workflow
does not decide whether a major is warranted or certify downstream compatibility.
This guidance does not schedule or promise a 4.0 release.

**2.0 historical import rename:** preferred import became **`picop`**. The `cypy` compatibility package and cimport mirrors were removed in 3.0; migrate both Python and Cython callers to `picop`. Pip distribution name was already `picop`.

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
3. [x] Tag `v1.0.0` (current releases use `picop-vX.Y.Z` tags).

### 2.0 import rename checklist

1. [x] Tree under `src/picop/`; historical soft `src/cypy/` shim + `DeprecationWarning`.
2. [x] Historical Cython cimport shims for `cypy` → `picop`.
3. [x] **3.0:** remove `cypy` Python package and cimport shims; require `picop` only. Rebuild downstream Cython extensions.

## Before tagging

| Step | Check |
|------|-------|
| 1 | On latest `main`; working tree clean |
| 2 | Review the changelog, compatibility impact, and release notes/title; confirm version/title before a real release |
| 3 | If any `docs/modules/` Lifecycle lines changed: `python scripts/grade_trackers.py` → all trackers grade A |
| 4 | Local smoke: `pip install -e . --no-build-isolation` then `from picop.hot import bytes_len, dict_get, str_len` |
| 5 | Examples: `for f in examples/py*.py examples/wrap_ansi.py; do python "$f"; done` |
| 6 | Export/compat: `python scripts/check_exports.py` |
| 7 | Confirm [`future/MONKEY.md`](future/MONKEY.md) is **not** wired into `src/picop` |
| 8 | Build/inspect release artifacts as below; check `publish.yml` matrix and workflow result |
| 9 | Update [`CHANGELOG.md`](../CHANGELOG.md) / [`README.md`](../README.md) status / [`COVERAGE.md`](../COVERAGE.md) if surface/policy changed |

Unless explicitly bypassed, `release.sh` runs export, tracker, shim and header
delta preflights (the header delta is skipped locally if no 3.15 interpreter is
available; CI covers it). It bumps version/changelog/install pins, commits,
pushes `main`, tags, creates a GitHub Release and watches publish. Its preflight
does not replace the full CI/release-artifact validation.

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

To promote a development version to stable, select the confirmed stable version
explicitly. Bump flags increment the numeric base of `X.Y.Z.devN` just as they
do for `X.Y.Z`; they do not promote a development version automatically.

The helper performs its own version bump and uses `picop X.Y.Z` as the GitHub
release title. If a release PR already merged and validated that exact version,
or the confirmed GitHub title differs, use the manual equivalent below rather
than bypassing checks or introducing a second metadata commit. Confirm the
full title, verify green CI on the exact `main` commit, and use
`gh release create <tag> --verify-tag --title "<confirmed full title>" --notes-file <notes-file>`.

Manual equivalent:

````bash
git checkout main && git pull
# after version bump is on main:
git tag -a "picop-vX.Y.Z" -m "picop X.Y.Z"
git push origin "picop-vX.Y.Z"
gh release create "picop-vX.Y.Z" --verify-tag --title "picop X.Y.Z" --notes-file - <<'EOF'
## Highlights
- …

## Requires
- Python ≥ 3.14

## Install
```bash
pip install "picop==X.Y.Z"
# or: pip install "picop @ git+https://github.com/ckirua/picop.git@picop-vX.Y.Z"
```
EOF
````

For release candidates, use the manual GitHub Release path: the helper does
not set GitHub prerelease/latest flags. After the confirmed version and notes
are on green `main`, create the annotated tag and GitHub prerelease with
`--prerelease --latest=false`. Pushing any `picop-v*` tag also triggers the
publish workflow; GitHub's prerelease flag does not suppress PyPI publication.
Do not use a candidate tag unless publishing that candidate to PyPI is intended.
To promote a candidate to stable later, select the confirmed stable version.


Pushing the tag runs the repository-root [`.github/workflows/publish.yml`](../.github/workflows/publish.yml) (Trusted Publishing → PyPI project **`picop`**). It builds one sdist and cibuildwheel wheels, validates the exact sdist on 3.14, 3.15, 3.14t and 3.15t, and publishes only after those validations and all wheel builds succeed. Python imports and Cython cimports use **`picop`**; the former `cypy` namespace was removed in 3.0.

### One-time PyPI Trusted Publisher

1. https://pypi.org/manage/account/publishing/ → pending publisher for **`picop`**
2. Owner `ckirua`, repo `picop`, workflow `publish.yml`, environment `pypi`
3. Optional: same on TestPyPI with environment `testpypi`
4. Create GitHub Environments `pypi` / `testpypi` (optional reviewers)

Test publication: Actions → **picop publish** → Run workflow → `testpypi`.
This uploads artifacts to TestPyPI; it is not a dry-run.

## Artifacts / local PyPI check

The publisher builds one source archive with CPython 3.15 and builds wheels with
cibuildwheel on configured Linux, Windows and macOS runners for the CPython
3.14/3.15 GIL and free-threaded ABI matrix in `pyproject.toml`. The exact sdist
is installed and tested in clean 3.14, 3.15, 3.14t and 3.15t environments
before publication; wheel builds run the configured pytest test command. This
does not mean every OS/architecture or downstream consumer is tested. Local
sdist commands below do not build release wheels.

```bash
pip install build twine
CPY_NATIVE=0 python3.15 -m build --sdist
twine check dist/*
smoke_dir="$(mktemp -d)"
python -m venv "$smoke_dir/venv"
CPY_NATIVE=0 "$smoke_dir/venv/bin/python" -m pip install "$(pwd)"/dist/picop-*.tar.gz
"$smoke_dir/venv/bin/python" -c "from picop.hot import bytes_len, dict_get, str_len; assert bytes_len(b'ok') == 2; assert dict_get({'a': 1}, 'a') == 1; assert str_len('ok') == 2"
PYTHON="$smoke_dir/venv/bin/python" bash scripts/smoke_barrel_cimport.sh
rm -rf "$smoke_dir"
# optional local upload (prefer CI Trusted Publishing):
# twine upload --repository testpypi dist/*
# twine upload dist/*
```

Repeat the installation and downstream consumer checks for all four runtimes.
On t runtimes, with `PYTHON_GIL` unset and no `-X gil` override, assert that
`sys._is_gil_enabled()` is false before and after importing the full `picop`
package and each native module. Verify that importing `cypy` is rejected. Separately run the full behavior suite
with `python -X gil=0 -m pytest tests -q`. A focused UUID-only import is not
evidence that the full package remains GIL-disabled.


## Post-release verify

```bash
pip install "picop==X.Y.Z"
python -c "from picop.hot import bytes_len; assert bytes_len(b'ok') == 2"
```
After publication, confirm the workflow succeeded, inspect the files listed for
the PyPI release, and perform this smoke check in a clean environment. The
install will use a compatible wheel when available; otherwise pip may build
from the sdist. This spot check is not a substitute for the four-ABI sdist
validation and does not establish downstream compatibility.

Portable builds are the default (`-O3` only). Contributors may set `CPY_NATIVE=1` for local tuned benches — do **not** require it for release artifacts.

## 3.0 consumer validation evidence

The 3.0 promotion used the genuine
[`ckirua/swissquote`](https://github.com/ckirua/swissquote/tree/05f08958b7eebfaec2ade4754997f1eb090d00d5)
Python client at `05f08958b7eebfaec2ade4754997f1eb090d00d5`, not picop's own
example extension. Its existing SBE market-data decoder directly cimports
`picop.cybytes.bas_string` / `blen` and `picop.cylist.lappend`. The project
already depends on `picop>=2.0.0`; no dependency or migration was manufactured.

Against the published `picop==3.0.0rc1`, independent source copies and clean
environments rebuilt the decoder for each ABI. All **13 existing offline
tests** passed on **3.14, 3.15, 3.14t and 3.15t**; forced `-X gil=0` runs also
passed all 13 tests on both t runtimes. A separate program decoded **1,000
golden SBE frames into 9,000 rows** per ABI, checked named SDK rows and rejected
a short frame without altering the destination. No live feed, credentials,
ClickHouse instance or C++ service was exercised.

**Threading boundary:** importing picop on both t runtimes left the GIL
disabled. Importing Swissquote's decoder then enabled it and emitted CPython's
warning because that extension does not declare free-threading compatibility.
Passing its forced-no-GIL tests does **not** establish a supported no-GIL
contract for Swissquote. Fixing or declaring that consumer's threading support
is separate work; do not suppress the warning or attribute it to picop.

Targeted RC source review found no confirmed release blocker. Comparing the
actual RC1 and local stable source archives found **162 package files**, with
only `src/picop/__about__.py` changed; no native fix required an RC2. This
record is pinned release evidence, not a new cross-repository CI dependency.

