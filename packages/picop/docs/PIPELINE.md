# Per-module full feature pipeline

Every module ships as its **own branch + PR**.  
**Commit/push when ready.** Maintainers may merge when the Before-merge checklist is green; external PRs need review.

Process docs live under [`docs/`](.) — trackers only under [`docs/modules/`](modules/). Status overview: [`README.md`](README.md#status-complete--not-an-open-backlog) (complete — not an open backlog).

## Stages (one Order)

```text
1. Branch     mod/NN-cy{name}  (from main) · remaster: fix/NN-cy{name} · Tier B: bench/… · polish: chore/… / docs/…
2. Index      v2 tracker if legacy/stub — full inventory, no skim
3. Measure    present / promoted: try-all + **depth investigation** (below)
4. Evidence   **must** update `docs/modules/NNN_cy{name}.md` — Bench results + Experiment conclusions (**no skip**; never “see harness” / “see PR” only)
5. Docs API   public PEP 257 summary (+ optional Notes) in `cy{name}.pyi`; lean `.pxd`
6. Tracker    ensure `docs/modules/NNN_cy{name}.md` Lifecycle / decisions match the PR
7. Ship       commit → push → PR (Short / Brief / Detailed + benches + probe notes)
8. Merge      when checklist green → next Order on a NEW branch (if any)
```

Absent / index-only Orders stop after stage 2 (+ lifecycle `indexed`) unless the user asks to promote.

## Measuring = try-all + depth (present / promoted)

**Not enough:** implement thin wrappers, run the default harness once, paste ratios only in the PR.  
**Required:** understand *why* results happen (CPython source / ABI / refcount / semantics), probe edge cases, and write that into the **module tracker** under **Experiment conclusions**. Exemplar depth: cytuple unique-ref; cybytes `memmem` scale + hybrid.

### Tracker update — mandatory (no skip)

Every measuring pass **must** edit `docs/modules/NNN_cy{name}.md` in the same change as code/benches:

| Section | Required content |
|---------|------------------|
| Workflow / Decision log | Every candidate → APPROVED / APPROVED (cimport) / REJECTED with evidence |
| **Bench results** | Timed table (mean±σ, p99, ratio, verdict) from the harness |
| **Experiment conclusions** | Depth findings (why/scale/safety/ABI/demotion) — not “see PR” |

Leaving the tracker stale while only updating the PR body or chat is a **process failure**. Do not merge until the tracker is current.

**Forbidden in trackers:** “see harness”, “see PR”, or empty Bench results placeholders. Paste the timed table (or explicit cimport/ABI `n/a` rows with mechanism notes) into `docs/modules/NNN_cy{name}.md`.

### Remaster branches (Phase 3 / Phase 4)

Depth remasters use `fix/NN-cy{name}` (or wave branches) from `main`. Same evidence bar as measuring.  
Tier B remasters use `bench/NN-cy{name}-tierb` (or wave `bench/phase4-*`) from `main` — paste Tier B tables; do not strip Tier A.
### For each inventory candidate

| Step | Action |
|------|--------|
| 1 | Implement a helper **or** smoke the raw API if a wrapper is impossible |
| 2 | Tier A bench (public) and/or record smoke / ABI failure |
| 3 | **Depth:** see checklist below — at least for winners, losers, and unsafe APIs |
| 4 | Decide with evidence in the tracker (decision log + Bench results + Experiment conclusions) |

**Do not** leave `TODO / no demand / deferred` as a silent skip.  
**Do not** mark APPROVED from a single happy-path ratio alone when behavior is subtle (uninit buffers, unique-ref, stolen refs, ABI gaps).  
**Do not** skip cheap sibling aliases (e.g. `Concat` + `ConcatAndDel`) — if the C-API exists and wrapping is a few lines, **alias it** for future Cython call sites; cost is near zero.

### Cheap aliases (compulsory when applicable)

When the mapped include has near-duplicate entry points (AndDel / checked vs macro / fixed arities already covered):

| Rule | Detail |
|------|--------|
| Wrap both | Prefer a thin `cdef`/`cpdef` alias rather than “call the other + DECREF yourself” |
| Still decide | APPROVED (cimport) is fine if unsafe from Python; do **not** REJECT as “redundant” without an alias |
| Document | One inventory + workflow row per alias |
| Checks (N3) | Prefer `{type}_check` / `{type}_check_exact` pairs; fold `str_is` ↔ `str_check_exact` in docs |
| Len vs size (N4) | `*_len` (typed) vs `*_size` (checked) are **semantic twins** — never identity-alias ([`docs/NAMING.md`](NAMING.md)) |

### Depth investigation checklist (required before merge)

Do these for the module under work (scale effort to risk; always cover primary + any REJECTED/cimport demotion):

| Probe | What to answer |
|-------|----------------|
| **Why win / lose** | Mechanism vs baseline (e.g. `memmem` vs `bytes_contains`, macro vs checked API) — cite CPython / libc when relevant |
| **Scale / shape** | At least 2–3 sizes or shapes (short vs long haystack, hit/miss, early/late match) — not only the primary toy payload |
| **Semantics / safety** | Uninitialized memory, stolen refs, mutable “immutable” builders, subtype checks |
| **Unique-ref / ownership** | If API requires refcnt==1 or steals: probe unique-in-C vs Python-held; document SystemError / segfault risk |
| **ABI / version** | Confirm symbol exists on target CPython (e.g. `nm` / headers); missing ⇒ REJECTED with evidence |
| **Demotion rationale** | If APPROVED (cimport) or REJECTED: one clear paragraph in Experiment conclusions |

Thin `Check` / `Size` wrappers may share one short note; hot paths and builders need real probes.

### Decision outcomes

| Outcome | When | Export |
|---------|------|--------|
| **APPROVED** | Gate pass **and** depth notes support safe public use | `cpdef` public |
| **APPROVED (cimport)** | Useful in Cython but fails public gate, needs unique-ref, or unsafe from Python | `cdef` / cimport only |
| **REJECTED** | Duplicate, missing ABI, unusable, or no keep rationale after try + depth | Remove or do not wrap; log why |

## Before merge (required on the worked module)

| Check | Done when |
|-------|-----------|
| Try-all | Every inventory candidate tried; no silent TODO |
| **Depth** | Depth checklist covered for primary + demotions/rejects |
| **Tracker updated** | `docs/modules/NNN_cy{name}.md` has current Bench results **and** Experiment conclusions (**no skip**) |
| **Public `.pyi` docs** | Every public `cpdef` has a PEP 257 **summary** (+ optional Notes; style below) |
| Lean `.pxd` | Cython/safety `#` comments only; `cdef` not in `.pyi` |
| Exports | `__init__.py` / `__init__.pxd` / `__all__` match decisions |
| QUEUE + PR | State updated; PR includes depth highlights |

Exemplar trackers: [`modules/001_cytuple.md`](modules/001_cytuple.md), [`modules/002_cybytes.md`](modules/002_cybytes.md).

### Public docstring style (`.pyi`)

| Rule | Detail |
|------|--------|
| Form | **Summary + optional Notes** (PEP 257): imperative first line; NumPy-style `Notes` for caveats |
| Skip | No `Args:` / `Parameters:` / `Returns:` / `Raises:` — signature + summary own types/outcomes |
| Add | Caveats in `Notes`: no bounds check, raises `IndexError`, uninit buffer, trusted-caller, vs builtin |
| Thin | Obvious `*_check` / `*_len` may stay **summary-only** (no Notes) |
| Sphinx | Napoleon enabled so `Notes` renders; stub→autodoc bridge in `doc/conf.py` |
| `.pxd` | No duplicate user prose — one-line `#` safety comments only |

```python
def dict_get(mp: dict, key: object, default: object = None) -> object:
    """Return ``mp[key]`` via ``PyDict_GetItemWithError``, or ``default``.

    Notes
    -----
    Prefer over ``mp.get`` on typed hot paths. Key lookup still uses
    normal hashing / equality.
    """
```

Shorter form still fine when the summary already carries the only caveat:

```python
def tuple_get(t: tuple, i: int) -> object:
    """Return ``t[i]`` via bounds-checked ``PyTuple_GetItem`` (raises ``IndexError``)."""
```

## Branch

| | |
|--|--|
| Name | `mod/NN-cy{name}` (Order `NN` from `docs/modules/NNN_cy{name}.md`); remaster `fix/…`; Tier B `bench/…` |
| Base | **`main`** (integration) — **always** `gh pr create --base main` |
| Scope | **One** module — tracker ± helpers ± `bench/cy{name}_bench.py` ± probe notes in tracker (Phase 5: packaging/docs/release only) |

```bash
git fetch origin
git checkout main && git pull
git checkout -b mod/14-cybytearray
```

## Bench

| Path | Role |
|------|------|
| `bench/cy{name}_bench.py` | Tier A harness (+ optional scale cases for depth) |
| `bench/tier_b/{name}_tb.pyx` + `bench/tier_b/{name}.py` | Tier B Cython-baseline microbench (Phase 4) |
| `bench/_bench_util.py` | Shared timing |
| `./bench/small.sh` | Run all Tier A `*_bench.py` |
| `./bench/tier_b/run.sh {name}` | Build + run one Tier B module (local) |
| `docs/modules/NNN_cy{name}.md` | **Results + Experiment conclusions** (source of truth) |

Gate: [`README.md`](README.md) · details: [`bench/BENCH.md`](../bench/BENCH.md).  
Phase 4 remasters use branch `bench/NN-cy{name}-tierb` (or wave `bench/phase4-*`) from `main`. Tier B is optional for measuring; when present, paste under Bench results without stripping Tier A.

## Open PR

Use [`.github/PULL_REQUEST_TEMPLATE.md`](../.github/PULL_REQUEST_TEMPLATE.md). Include depth findings in Detailed (not only ratio tables).

## Allowed without confirmation

| Action | OK? |
|--------|-----|
| Commit / push on module branch | **Yes** |
| Open / update PR | **Yes** |
| **Merge** to `main` | Maintainers after Before-merge checklist; external PRs need review |

After merge: next Order on a **new** branch from updated `main` (if any).

## Phase 5 (product polish) — complete

Packaging, README/examples, and release checklist — see [`RELEASE.md`](RELEASE.md) / [`README.md`](README.md#status-complete--not-an-open-backlog) status.  
**Out of prod:** [`future/MONKEY.md`](future/MONKEY.md) stays archive-only — do not restore builtin monkey-patches into `src/cypy`.

## Phase 6 (usage examples) — complete

Every Order has a runnable **python** example, a **cython** recipe pointer, or honest **n/a** — see [`examples/README.md`](../examples/README.md).  
CI runs `scripts/grade_trackers.py` (53/53 A) and all `examples/py*.py`. Do not invent pure-Python demos for cimport-only modules.
