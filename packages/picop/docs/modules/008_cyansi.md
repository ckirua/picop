# cyansi

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | custom (terminal SGR) — not CPython |
| Sources | `src/cypy/cyansi.pxd`, `cyansi.pyx`, `cyansi.pxi`, `cyansi.pyi` |
| Surface | public |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full (declared custom surface) |

## Why

Interned SGR builders + CSI strip for terminal UIs. Built on `cyunicode.uintern`.

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| reset / fg8 / bg8 / fg256 / bold / wrap | cypy | cpdef | public | interned tables for common codes |
| strip_ansi | cypy | cpdef | public | single-pass CSI strip |
| RESET / FOREGROUND_* / BACKGROUND_* / BOLD_* | cypy | py | public | module constants/classes |
| CPython unicode / bytes | — | — | — | N/A — custom module |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| fg8 | APPROVED | primary table hit **0.25x** |
| bg8 / fg256 | APPROVED | **0.28x** table |
| bold / reset / wrap | APPROVED | **0.71–0.79x** |
| strip_ansi | APPROVED | CSI **0.32x**; plain **0.59x** |
| miss-path fmt | APPROVED | still **0.64–0.66x** vs f-string |

## Lifecycle

| Field | Value |
|-------|--------|
| Freeze | **1.0 Core** — public + documented cimport; see COVERAGE § 1.0 freeze |
| Iteration | 1 |
| Last pass | 2026-07-21 — Phase 4 Tier B (Cython baseline) |
| Next action | — |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| fg8 table | Intern beat f-string | `bench/cyansi_bench.py` | **0.25x** | APPROVED | 1 |
| strip_ansi | Beat regex | same | **0.32x** | APPROVED | 1 |
| all builders | — | same | 0.25–0.79x | APPROVED | 1 |

## Bench notes

- Harness: [`bench/cyansi_bench.py`](../../bench/cyansi_bench.py)
- Env: CPython 3.14.6 · Linux x86_64 · GIL on · N=80000 RUNS=5

## Bench results

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| fg8 | table hit | 1.04±0.01ms | 1.05ms | 0.25x | 0.25x | pass |
| fg8 | miss fmt | 2.51±0.04ms | 2.57ms | 0.64x | 0.62x | pass |
| bg8 | table hit | 1.09±0.10ms | 1.25ms | 0.28x | 0.33x | pass |
| fg256 | table hit | 1.07±0.04ms | 1.14ms | 0.28x | 0.29x | pass |
| fg256 | miss fmt | 2.67±0.13ms | 2.88ms | 0.66x | 0.71x | pass |
| bold | on | 1.01±0.01ms | 1.02ms | 0.73x | 0.73x | pass |
| reset | reset | 0.92±0.05ms | 0.98ms | 0.71x | 0.75x | pass |
| wrap | wrap | 3.01±0.07ms | 3.10ms | 0.79x | 0.80x | pass |
| strip_ansi | with CSI | 6.65±0.01ms | 6.66ms | 0.32x | 0.32x | pass |
| strip_ansi | no CSI | 3.20±0.07ms | 3.29ms | 0.59x | 0.60x | pass |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cyansi.py`](../../bench/tier_b/cyansi.py) · `cyansi_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| fg8 | table hit 31 | 0.36±0.00ms | 0.37ms | 3.51±0.09ms | **0.10x** | 0.10x | cypy faster |
| bg8 | table hit 41 | 0.36±0.00ms | 0.36ms | 3.48±0.04ms | **0.10x** | 0.10x | cypy faster |
| bold | on | 0.30±0.01ms | 0.31ms | 0.08±0.00ms | **3.94x** | 3.85x | baseline faster |

**Tier B takeaway:** primary `fg8` **0.10x** vs f-string — table lookup dominates format baseline.

## Experiment conclusions

**Tier B:** primary `fg8` **0.10x** vs f-string — table lookup dominates format baseline.

- **Why win:** table lookups return pre-`uintern`’d immortal-ish strings — no f-string / format each call. Miss paths still beat f-strings (**0.64x**).
- **strip_ansi:** hand-rolled CSI scan beats `re.sub` (**0.32x** with escapes; **0.59x** identity fast-path when no ESC).
- **Safety:** strip handles CSI final byte `0x40–0x7E`; non-CSI ESC left intact. Tables init once under GIL.
- **Free-threaded:** init is idempotent; interned SGR strings are safe to share across threads after first `reset()`/`fg8` touch.

## Done when

- [x] Full custom inventory
- [x] Bench results + Experiment conclusions
- [x] Public `.pyi` one-liners; `__all__: tuple[str, ...]`
