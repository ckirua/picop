# cyunicode

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.unicode` (UTF-8 / intern slice; high-level str → [`006_cystr.md`](006_cystr.md)) |
| Sources | `src/picop/cyunicode.pxd`, `cyunicode.pyx`, `cyunicode.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full (declared slice) |

## Why

Zero-copy UTF-8 borrow + intern for Cython; public owning `bytes` / `uintern` for benches and `cyansi`.

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| uutf8 | cypy | cdef | cimport | borrowed `AsUTF8` — do not outlive `s` |
| uutf8_and_size | cypy | cdef | cimport | borrowed + length |
| uutf8_eq | cypy | cdef | cimport | size + `memcmp` on UTF-8 views; lifetime = `a`/`b` |
| uutf8_bytes | cypy | cpdef | public | owning `AsUTF8String` |
| uintern_in_place | cypy | cdef | cimport | mutates `PyObject**` slot |
| uintern | cypy | cpdef | public | intern + return |
| unicode_from_string | cypy | cdef | cimport | `PyUnicode_FromString` — no intern; mirror `bytes_from_string` |
| unicode_eq | cypy | cpdef | public | thin alias of `str_eq`; soft `ueq` |
| uintern_from_string | cypy | cdef | cimport | `PyUnicode_InternFromString` sibling |
| PyUnicodeWriter_* | C-API | `cdef class` | public | Order 073: `UnicodeWriter` incremental str builder (CPython 3.11+); `write` / `write_char` / `write_ascii` / `write_repr` / `write_substring` / `write_utf8` / `finish` / `discard`; context-manager; double-finish raises `RuntimeError` |
| PyBytesWriter_* | C-API | tried | — | sibling bytes builder — deferred to a later Order (see decision log) |
| codecs / From* / New / … | C-API | tried | — | out of slice → cystr deferred / REJECTED scope |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| uutf8 / uutf8_and_size | APPROVED (cimport) | zero-copy; unsafe from Python |
| uutf8_eq | APPROVED (cimport) | UTF-8 size+memcmp; issue #17 |
| uutf8_bytes | APPROVED | **0.95–1.01x** vs `encode` — clarity / owning mirror |
| uintern | APPROVED | **1.04–1.05x** vs `sys.intern` — clarity; used by cyansi |
| unicode_from_string | APPROVED (cimport) | ordinary C→str; no intern; issue #1 |
| unicode_eq | APPROVED | alias of `str_eq` (issue #14); no divergent semantics |
| uintern_in_place / uintern_from_string | APPROVED (cimport) | slot / C-string siblings |
| UnicodeWriter | APPROVED | Order 073: beats `+=` (0.74x), loses to `''.join` on materialized parts (5.16x) — streaming builder, documented in PERF_PARITY |
| remainder unicode | REJECTED (scope) | not this slice |

## Lifecycle

| Field | Value |
|-------|--------|
| Freeze | **1.0 Core** — public + documented cimport; see COVERAGE § 1.0 freeze |
| Iteration | 3 |
P26-07-22 — `*_eq` inventory Tier A (`cyeq_inventory_bench`)|
P26-11-12 — Order 073 `UnicodeWriter`: builder vs join/`+=`, cdef-loop Tier B, 3.14/3.15 CI|
| Next action | PyBytesWriter sibling in a later Order |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| uutf8_bytes | Beat encode | `bench/cyunicode_bench.py` | ~1.0x | APPROVED (clarity) | 1 |
| uintern | Match sys.intern | same | ~1.05x | APPROVED (clarity) | 1 |
| uutf8* | Zero-copy | smoke/docs | borrowed | APPROVED (cimport) | 1 |
| unicode_from_string | Cheap C→str | smoke (cimport) | thin alias | APPROVED (cimport) | 2 |
| UnicodeWriter | Incremental build beats join/`+=`? | Tier A builder bench + Tier B cdef loop | 0.74x vs `+=`; 5.16x vs `join`; 1.55x cdef loop vs append+join | APPROVED (streaming niche) | 3 |
| PyBytesWriter_* | Same story for bytes | — | sibling builder, scheduled for a later Order | DEFERRED | 3 |

## Bench notes

- Harness: [`bench/cyunicode_bench.py`](../../bench/cyunicode_bench.py)
- Env: CPython 3.14.6 · Linux x86_64 · GIL on · N=80000 RUNS=5

## Bench results

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| uutf8_bytes | short | 1.51±0.06ms | 1.60ms | 1.01x | 1.04x | tie |
| uutf8_bytes | n=64 | 1.43±0.03ms | 1.47ms | 0.95x | 0.89x | pass |
| uutf8_bytes | n=4k | 4.36±0.21ms | 4.72ms | 1.01x | 1.08x | tie |
| uutf8_bytes | non-ascii | 2.64±0.05ms | 2.73ms | 1.00x | 1.03x | tie |
| uintern | already | 1.03±0.05ms | 1.12ms | 1.05x | 1.10x | clarity |
| uintern | short | 1.05±0.03ms | 1.10ms | 1.05x | 1.00x | clarity |
| uintern | non-ascii | 1.03±0.02ms | 1.05ms | 1.04x | 0.95x | clarity |
| unicode_from_string | ascii / empty / non-ascii | — | — | n/a (cimport) | — | smoke OK |

### UnicodeWriter (Order 073 builder bench)

Harness: [`bench/cyunicode_bench.py`](../../bench/cyunicode_bench.py) · CPython 3.14.7 · Linux x86_64 · 80,000 short parts per build, 20 builds sampled × `runs=5`. Ratio = builder using `UnicodeWriter` / plain-Python builder.

| operation | baseline | writer mean±σ | baseline mean±σ | ratio | verdict |
|-----------|----------|---------------|-----------------|-------|---------|
| UnicodeWriter(hint) | `''.join(parts)` | 57.67±0.41ms | 11.13±0.19ms | **5.18x** | join wins — parts already materialized |
| UnicodeWriter(no hint) | `''.join(parts)` | 58.03±0.24ms | 11.40±0.18ms | **5.09x** | join wins |
| UnicodeWriter(no hint) | `s += p` loop | 58.30±0.48ms | 77.53±0.38ms | **0.75x** | writer wins (+25%) |

**Tier B — `UnicodeWriter` in a cdef loop** (`bench/tier_b/cyunicode.py` + `cyunicode_tb.pyx`, N=2,000,000 parts): `cypy_writer` 7.23±0.75ms vs typed `list.append`+`join` baseline 4.85±0.92ms → **1.49x** (p99 1.29x). **Informational.**

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cyunicode.py`](../../bench/tier_b/cyunicode.py) · `cyunicode_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| uutf8_bytes | short | 11.18±0.01ms | 11.20ms | 11.22±0.04ms | **1.00x** | 0.99x | ~tie |
| uintern | already | 4.20±0.01ms | 4.22ms | 3.84±0.03ms | **1.09x** | 1.08x | baseline faster |

**Tier B takeaway:** `uutf8_bytes` **1.00x** vs `AsUTF8String` — thin wrapper parity.


### `*_eq` inventory (Tier A depth)

Harness: [`bench/cyeq_inventory_bench.py`](../../bench/cyeq_inventory_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| unicode_eq | ascii eq | 0.96±0.03ms | 1.01ms | **0.64x** | 0.63x | APPROVED |
| unicode_eq | ascii ne | 1.11±0.05ms | 1.22ms | **0.67x** | 0.70x | APPROVED |
| unicode_eq | non-ascii eq | 0.96±0.03ms | 1.03ms | **0.64x** | 0.65x | APPROVED |
### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| unicode_eq | ascii eq | 2.54±0.02ms | 2.58ms | 2.53±0.01ms | **1.00x** | 1.01x | ~tie |
| unicode_eq | non-ascii eq | 2.54±0.03ms | 2.58ms | 2.53±0.01ms | **1.00x** | 1.01x | ~tie |

**Tier B `*_eq` notes:**
- **`unicode_eq`:** ~tie (**1.00x**) vs typed Cython `str == str` (same family as `str_eq`).

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. ~tie (**1.00x**) vs typed Cython `str == str` (same family as `str_eq`).

**Tier B:** `uutf8_bytes` **1.00x** vs `AsUTF8String` — thin wrapper parity.

- **Why public ~tie:** `AsUTF8String` / `InternInPlace` are the same C entry points `str.encode` / `sys.intern` use; Python→cpdef adds little. Real win is **cdef `uutf8`** zero-copy borrow in Cython (not tier-A measurable).
- **Safety:** borrowed `uutf8*` must not outlive `s`; invalidate if `s` is resized. `uintern_in_place` needs a mutable `PyObject**` — not safe as a naive Python call. C-string helpers take NUL-terminated `const char *` (not Python `str`); NULL is undefined (same as raw C-API).
- **Alias:** `unicode_from_string` wraps `PyUnicode_FromString` (owning `str`, **no** intern). `uintern_from_string` wraps `PyUnicode_InternFromString`. Prefer the former for ordinary C→str (toml keys, path fragments); reserve intern for table/cold-path identity.
- **Demotion:** `unicode_from_string` is **APPROVED (cimport)** — `const char *` is not a Python-callable surface; mirrors `bytes_from_string` (not on `cypy.hot` / buffers).
- **Free-threaded:** intern table is runtime-shared; prefer intern at module-init / cold paths (as `cyansi` tables do). Non-interning `unicode_from_string` has no intern-table contention.
- **UnicodeWriter crossover (Order 073):** `''.join` is a single C pass over a materialized list (~7 ns/part) and beats the writer's per-call `write` (~36 ns from Python, ~14.5 ns in a `cdef` loop vs append+join). The writer's niche is **streaming** builds where no part list exists: it beats `s += p` by ~25% and stays O(1) extra memory instead of O(parts). `max_size` hint does not close the join gap (5.18x vs 5.09x). Lifecycle is strict: `finish()`/`discard()` consume the handle, further calls raise `RuntimeError` (no UB), and `__exit__` discards an open writer — use the context manager.
- **WriteASCII signature:** CPython 3.14+ `PyUnicodeWriter_WriteASCII` takes `(writer, const char *, size)` — the wrapper passes `text` + length; the simplified two-arg spelling in the CPython docs snapshot is stale.
- **Safety:** the writer owns its internal buffer; an unclosed writer leaks the buffer until GC and a finished writer must never be reused (`finish()` invalidates the handle — NULL-checked guard raises `RuntimeError`).

## Done when

- [x] Full inventory of declared slice
- [x] Workflow + decision log
- [x] Bench results + Experiment conclusions
- [x] Public `.pyi` one-liners; lean `.pxd`
- [x] `unicode_from_string` (issue #1) — cimport + smoke
- [x] Order 073: `UnicodeWriter` class, tests, builder bench (Tier A + B), PERF_PARITY row, example + cimport smoke
