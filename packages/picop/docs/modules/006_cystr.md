# cystr

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | custom high-level `str` surface over `cpython.unicode` (UTF-8/intern → [`007_cyunicode.md`](007_cyunicode.md)) |
| Sources | `src/cypy/cystr.pxd`, `cystr.pyx`, `cystr.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full (declared custom surface) |

## Why

Hot-path equality, contains, coerce/guards, concat, and ASCII classifiers for typed exact `str`. Not a full `unicode.pxd` wrap — codecs/builders/wide-char live elsewhere or stay deferred.

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| ucheck | cypy | cpdef | public | `PyUnicode_Check` |
| ucheck_exact | cypy | cpdef | public | `PyUnicode_CheckExact` |
| is_str | cypy | cpdef | public | `type is str` |
| is_not_str | cypy | cpdef | public | negated |
| as_str_or_empty / none_to_empty / str_or_none / str_or_empty | cypy | cpdef | public | coerce helpers |
| strlen | cypy | cpdef | public | `GET_LENGTH` — clarity vs `len` |
| is_empty / not_empty | cypy | cpdef | public | length predicates |
| scmp / str_cmp | cypy | cpdef | public | three-way -1/0/1; soft `str_compare` |
| slt/sle/sgt/sge | cypy | cpdef | public | ordering via `str_cmp`; preferred `str_lt`/`le`/`gt`/`ge` |
| streq / strneq | cypy | cpdef | public | 1BYTE `memcmp` / Compare |
| startswith / endswith | cypy | cpdef | public | 1BYTE `memcmp` / Tailmatch |
| contains | cypy | cpdef | public | 1BYTE `memchr`/`memmem` / Find |
| find | cypy | cpdef | cimport | loses vs `str.find` on tier A |
| char_at / first_char / last_char | cypy | cpdef | public | `PyUnicode_READ` unchecked |
| concat / concat3 / concat4 | cypy | cpdef | public | `PyUnicode_Concat` chains |
| is_blank / all_digits / all_alpha_ascii / all_alnum_ascii | cypy | cpdef | public | ASCII scans |
| is_ascii | cypy | cpdef | cimport | loses badly vs `str.isascii` on long ASCII |
| PyUnicode_* codecs / From* / New / Split / Join / … | C-API | tried | — | out of cystr scope; see deferred |
| UTF-8 / Intern* | C-API | — | — | owned by `cyunicode` |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| contains | APPROVED | primary short **0.75x**; mid **0.85x**; **4k loses 1.16x** (scale) |
| streq / strneq | APPROVED | **0.66–0.69x** |
| scmp / str_cmp | APPROVED | `PyUnicode_Compare` → -1/0/1 (issue #15) |
| str_lt/le/gt/ge | APPROVED | thin wrappers on `str_cmp` (issue #16) |
| guards / coerce / empty | APPROVED | **0.37–0.59x** |
| char_* / concat* | APPROVED | **0.47–0.83x** |
| classifiers (blank/digits/alpha/alnum) | APPROVED | **0.40–0.49x** |
| endswith | APPROVED | hit **0.99x** tie; miss loses — keep sibling of startswith |
| startswith / strlen | APPROVED | clarity / Cython entry (**1.05–1.13x** / **1.08x** from Python) |
| ucheck / ucheck_exact | APPROVED | cheap Check aliases |
| find | APPROVED (cimport) | **1.03–1.29x** vs `str.find` |
| is_ascii | APPROVED (cimport) | long ASCII **1.97x** vs `str.isascii`; non-ASCII reject **0.59x** |
| full unicode codecs/builders | REJECTED (scope) | not cystr’s surface |

## Lifecycle

| Field | Value |
|-------|--------|
| Freeze | **1.0 Core** — public + documented cimport; see COVERAGE § 1.0 freeze |
| Iteration | 1 |
| Last pass | 2026-07-22 — str_order inventory (Tier A+B) |
| Next action | — |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| contains | memmem/Find beat `in` | `bench/cystr_bench.py` | 0.75x short; 1.16x 4k | APPROVED | 1 |
| streq / guards / concat / classifiers | hot helpers | same | 0.37–0.83x | APPROVED | 1 |
| find / is_ascii | promote | same | 1.29x / 1.97x | APPROVED (cimport) | 1 |
| ucheck* | cheap Check | smoke | aliases of is_str family | APPROVED | 1 |

## Bench notes

- Harness: [`bench/cystr_bench.py`](../../bench/cystr_bench.py)
- Primary: `contains` hit short ASCII
- Env: CPython 3.14.6 · Linux x86_64 · GIL on · N=80000 RUNS=5

## Bench results

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| contains | hit short | 1.39±0.03ms | 1.44ms | 0.75x | 0.71x | pass |
| contains | miss short | 1.15±0.02ms | 1.17ms | 0.68x | 0.68x | pass |
| contains | hit mid | 1.82±0.12ms | 2.01ms | 0.85x | 0.92x | pass |
| contains | hit 4k | 20.29±0.09ms | 20.42ms | 1.16x | 1.15x | scale lose |
| contains | non-ascii | 1.14±0.03ms | 1.18ms | 0.67x | 0.69x | pass |
| find | hit mid | 1.73±0.05ms | 1.79ms | 1.03x | 0.96x | cimport |
| find | miss mid | 2.79±0.87ms | 4.26ms | 1.29x | 1.95x | cimport |
| startswith | hit | 1.10±0.08ms | 1.20ms | 1.05x | 1.12x | clarity |
| startswith | miss | 1.09±0.05ms | 1.17ms | 1.13x | 1.11x | clarity |
| endswith | hit | 1.04±0.03ms | 1.08ms | 0.99x | 0.96x | tie |
| endswith | miss | 1.08±0.02ms | 1.11ms | 1.16x | 1.18x | clarity |
| streq | eq same | 0.96±0.04ms | 1.02ms | 0.67x | 0.69x | pass |
| streq | ne | 1.09±0.01ms | 1.09ms | 0.67x | 0.63x | pass |
| streq | non-ascii eq | 0.98±0.04ms | 1.01ms | 0.66x | 0.63x | pass |
| strneq | ne | 1.07±0.02ms | 1.10ms | 0.69x | 0.68x | pass |
| strlen | n=70 | 0.96±0.01ms | 0.97ms | 1.08x | 1.09x | clarity |
| is_empty | empty | 0.86±0.01ms | 0.87ms | 0.48x | 0.45x | pass |
| not_empty | nonempty | 0.90±0.01ms | 0.91ms | 0.50x | 0.50x | pass |
| is_str | str | 0.90±0.03ms | 0.93ms | 0.37x | 0.21x | pass |
| is_not_str | int | 0.89±0.01ms | 0.91ms | 0.53x | 0.51x | pass |
| as_str_or_empty | str | 0.94±0.02ms | 0.97ms | 0.52x | 0.51x | pass |
| none_to_empty | None | 0.87±0.00ms | 0.88ms | 0.59x | 0.58x | pass |
| str_or_none | int | 0.86±0.02ms | 0.88ms | 0.50x | 0.49x | pass |
| str_or_empty | empty str | 0.99±0.02ms | 1.03ms | 0.53x | 0.51x | pass |
| char_at | i=1 | 1.10±0.03ms | 1.14ms | 0.62x | 0.61x | pass |
| first_char | first | 0.97±0.04ms | 1.04ms | 0.54x | 0.55x | pass |
| last_char | last | 0.99±0.05ms | 1.07ms | 0.47x | 0.47x | pass |
| concat | 2 | 1.76±0.08ms | 1.87ms | 0.80x | 0.85x | pass |
| concat3 | 3 | 2.63±0.09ms | 2.73ms | 0.83x | 0.84x | pass |
| concat4 | 4 | 3.31±0.05ms | 3.37ms | 0.81x | 0.81x | pass |
| is_ascii | ascii mid | 3.09±0.05ms | 3.17ms | 1.97x | 1.95x | cimport |
| is_ascii | non-ascii | 0.95±0.01ms | 0.95ms | 0.59x | 0.55x | (reject path) |
| is_blank | ws | 0.95±0.01ms | 0.97ms | 0.49x | 0.48x | pass |
| all_digits | digits | 0.99±0.01ms | 1.00ms | 0.40x | 0.39x | pass |
| all_alpha_ascii | alpha | 1.04±0.02ms | 1.06ms | 0.44x | 0.44x | pass |
| all_alnum_ascii | alnum | 0.99±0.03ms | 1.03ms | 0.40x | 0.40x | pass |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cystr.py`](../../bench/tier_b/cystr.py) · `cystr_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| contains | short hit | 4.99±0.05ms | 5.07ms | 5.72±0.02ms | **0.87x** | 0.88x | cypy faster |
| streq | equal | 2.52±0.01ms | 2.53ms | 2.53±0.01ms | **1.00x** | 0.99x | ~tie |
| strlen | short | 2.98±0.19ms | 3.24ms | 2.99±0.09ms | **1.00x** | 1.05x | ~tie |
| is_str | str | 2.87±0.11ms | 3.02ms | 2.83±0.16ms | **1.01x** | 0.98x | ~tie |

**Tier B takeaway:** primary `contains` **0.87x** vs typed `in` — still ahead of Cython emit on short hit.

### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| str_eq | eq ascii | 2.52±0.01ms | 2.54ms | 2.53±0.01ms | **1.00x** | 1.00x | ~tie |
| str_eq | ne ascii | 4.19±0.05ms | 4.26ms | 2.59±0.02ms | **1.61x** | 1.63x | baseline faster |

**Tier B `*_eq` notes:**
- **`str_eq`:** Equal ~tie; ne ascii **1.61x** lose vs Cython `str == str` (unicode compare path). Tier A win is Python overhead.

### str_order inventory (Tier A + B)

Harness: [`bench/cystr_order_inventory_bench.py`](../../bench/cystr_order_inventory_bench.py) · Tier B [`bench/tier_b/cystr_order.py`](../../bench/tier_b/cystr_order.py).

| operation | ratio A | ratio B | note |
|-----------|---------|---------|------|
| `str_cmp` | **0.50–0.56x** | **0.26x** | pass |
| `str_lt`/`le`/`gt`/`ge` | **0.58–0.72x** | **0.47–0.63x** | pass |
| `str_check` / `str_is` | **0.40–0.57x** | ~tie | Tier A win is call overhead |

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. Equal ~tie; ne ascii **1.61x** lose vs Cython `str == str` (unicode compare path). Tier A win is Python overhead.

**str_order inventory:** `str_cmp` / ordering gate-pass; Tier B `str_cmp` **0.26x** vs typed three-way.

**Tier B:** primary `contains` **0.87x** vs typed `in` — still ahead of Cython emit on short hit.

- **Why contains wins (short/mid):** 1BYTE `memchr`/`memmem` avoids unicode find setup; non-ASCII falls back to `PyUnicode_Find` and still **0.67x** on small.
- **Scale:** 4k haystack **1.16x** — CPython `in` specializes; same class of scale loss as cybytes `memmem` on huge haystacks. Prefer `contains` for short/medium ASCII needles.
- **`is_ascii` demotion:** `str.isascii()` is a tight C builtin; our KIND loop is **1.97x** on long ASCII. Fast only on early non-ASCII reject (**0.59x**). Keep **cimport** for Cython callers that already branch on kind.
- **`find` demotion:** thin `PyUnicode_Find` wrapper loses to `str.find` from Python (**1.03–1.29x**).
- **Safety:** `char_at` / `first_char` / `last_char` are unchecked READ — empty/`i` OOB is UB; document in `.pyi`.
- **Cheap aliases:** `ucheck` / `ucheck_exact` added beside `is_str`.
- **Scope:** full `unicode.pxd` codecs/From*/Split/Join/Replace left deferred; UTF-8/intern → cyunicode. Free-threaded: helpers are read-mostly on immortal/shared str; mutators N/A.

## Done when

- [x] Full inventory vs declared custom surface
- [x] Every row has workflow status
- [x] Lifecycle + next action filled
- [x] APPROVED / APPROVED (cimport) rows have decision-log evidence
- [x] REJECTED / scope rows logged
- [x] Bench results + Experiment conclusions in **this** file
- [x] Public PEP 257 one-liners in `cystr.pyi`; lean `.pxd`
