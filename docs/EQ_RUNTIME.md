# Runtime / embedding `*_eq` stretch (issue #44)

Inventory for Runtime modules: ship `*_eq` **only** when there is a clear
micro-opt or API-symmetry win. Most Runtime surfaces are procedural or
identity-only — prefer [`obj_eq`](modules/026_cyobject.md) rather than thin
per-type wrappers.

Status key: **done** · **skip** · **n/a** (no comparable value type)

| Module | Decision | Notes |
|--------|----------|-------|
| `cyobject` | **done** | `obj_eq` (#35) — generic richcompare EQ |
| `cydatetime` | **done** | `dt_date_eq` / `dt_time_eq` / `dt_datetime_eq` / `dt_timedelta_eq` |
| `cyweakref` | **done** | `weakref_eq` (#38) |
| `cypycapsule` | **done** | `capsule_eq` (#38) — identity |
| `cycellobject` | **done** | `cell_eq` |
| `cyfunction` / `cymethod` / `cymodule` / `cygenobject` / `cyiterator` | **done** | identity / method richcompare (#40–#41 batch) |
| `cycontextvars` | **done** | `context_eq` — `Context` has mapping value equality; soft `ctxeq`. **Skip** dedicated `ContextVar` / `Token` eq (identity → `obj_eq`) |
| `cyansi` | **skip** | SGR builders; no value type to compare |
| `cygc` | **skip** | procedural GC controls |
| `cyerr` | **skip** | exception / error API; not value equality |
| `cymem` | **skip** | allocator / raw memory |
| `cythread` | **skip** | threading primitives |
| `cyatomic` | **skip** | atomics; compare via typed loads, not object eq |
| `cymarshal` | **skip** | serialize/deserialize; compare payloads with typed eqs |
| `cyfileobject` | **skip** | file handles; identity/`obj_eq` if needed |
| `cyceval` | **skip** | eval / frame plumbing |
| `cypystate` | **skip** | interpreter state |
| `cypylifecycle` | **skip** | init/fini |
| `cypyport` | **skip** | portability macros / helpers |
| `cyconversion` | **skip** | C converters; not Python objects |
| `cyversion` | **skip** | version constants / queries |
| `cytime` | **skip** | thin clock wrappers return floats — use `float_eq` / stdlib |
| `cycodecs` | **skip** | codec registry / encode paths; no standalone eq type |
| `cyref` / `cygetargs` / `cylongintrepr` | **skip** | embedding footguns; no public value-eq surface |

## Shipped in this stretch close-out

- `context_eq` (`cycontextvars`) — only new Runtime helper justified here.

## Explicit non-goals

- No `code_eq` without a `cycode` module (already noted under misc eq batch).
- No mass identity wrappers that only alias `obj_eq`.

Closes the acceptance checklist for [#44](https://github.com/ckirua/picop/issues/44).


## Bench follow-up (2026-07-22)

Shipped helpers above were re-measured (no smoke placeholders):

| Helper | Primary Tier A ratio | Harness |
|--------|----------------------|---------|
| `context_eq` | **0.55–0.81x** | `bench/cycontextvars_bench.py` |
| identity misc (`func_eq` … `capsule_eq`) | **0.53–0.68x** | `bench/cyeq_misc_bench.py` |

Skip decisions above are unchanged — no new Runtime eq wrappers.
