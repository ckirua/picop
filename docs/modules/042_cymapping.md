# cymapping

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.mapping` |
| Sources | `src/cypy/cymapping.pxd`, `.pyx`, `.pyi` |
| Surface | public |
| Tracker lifecycle | decided |
| Format | v2 |
| Indexed | full |

## Why

Abstract mapping protocol. Prefer ``cydict`` when type known.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| map_check / len / has_key* / del* / keys / values / items / getitem_string / setitem_string | public (cpdef) | `map_len` stub-hidden (Tier A `>1.02x` vs `len`) |
| mapeq | public | identity/size + richcompare; preferred `map_eq` |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| map_check / has_key / getitem_string | APPROVED | see benches |
| map_len | APPROVED (API) | Tier A **~1.10x** vs `len` — stub-hidden from `.pyi` |
| map_keys | APPROVED | Tier A win vs `list(o.keys())` — remains stubbed |
| mapeq / map_eq | APPROVED | identity/size + richcompare (issue #24) |

## Lifecycle

| Field | Value |
|-------|--------|
| Freeze | **Provisional (Protocols)** after 1.0 — not Core; may evolve under minors |
| Iteration | 1 |
| Last pass | 2026-08-02 — stub-hide Tier A `>1.02x` from `.pyi` |
| Next action | — |

## Decision log

| Symbol | Ask | Evidence | Decision | Iter |
|--------|-----|----------|----------|------|
| mapeq | Abstract `==` | identity/size + richcompare | APPROVED | 1 |

## Bench notes

- Harness: [`bench/cymapping_bench.py`](../../bench/cymapping_bench.py)

## Bench results

Harness: [`bench/cymapping_bench.py`](../../bench/cymapping_bench.py) · tier A · CPython 3.14 · N=80_000

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| map_check | dict | **0.16x** | APPROVED |
| map_check | list (miss) | **0.18x** | APPROVED |
| map_len | dict | **1.03x** | APPROVED (API) |
| map_has_key | hit | **0.71x** | APPROVED |
| map_getitem_string | key | **0.67x** | APPROVED |
| map_keys | dict | **0.51x** | APPROVED |

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cymapping.py`](../../bench/tier_b/cymapping.py) · `cymapping_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| map_check | hit | 2.92±0.01ms | 2.93ms | 2.49±0.02ms | **1.17x** | 1.16x | baseline faster |

**Tier B takeaway:** primary `map_check` **1.17x** vs typed Cython baseline (hit).



### `*_eq` inventory (Tier A depth)

Harness: [`bench/cyeq_inventory_bench.py`](../../bench/cyeq_inventory_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| map_eq | dict eq | 2.02±0.03ms | 2.06ms | **0.79x** | 0.76x | APPROVED |
| map_eq | dict ne | 2.19±0.06ms | 2.31ms | **0.82x** | 0.81x | APPROVED |
### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| map_eq | dict eq | 24.95±0.27ms | 25.16ms | 22.99±0.07ms | **1.09x** | 1.09x | baseline faster |
| map_eq | dict ne | 28.69±0.10ms | 28.83ms | 27.11±0.57ms | **1.06x** | 1.03x | baseline faster |

**Tier B `*_eq` notes:**
- **`map_eq`:** **Lose 1.06–1.09x** — abstract mapping path; prefer `dict_eq` when typed.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. **Lose 1.06–1.09x** — abstract mapping path; prefer `dict_eq` when typed.

**Tier B:** `map_check` **1.16x** vs isinstance(dict) — Mapping check is broader.

| Topic | Finding |
|-------|---------|
| Why checks win | Mapping flag / abstract check beats `isinstance(Mapping)` |
| Why prefer typed | When dict known, `cydict` (`dget`/`dcontains`/`dict_eq`) avoids abstract protocol dispatch |
| `map_eq` | Same semantics as `==` (identity/size short-circuit then richcompare); prefer `dict_eq` when typed |
| Scale | Abstract ops stay O(1) wrapper cost; large maps dominated by hash lookup either way |
| Safety | `HasKey` never raises on miss (unlike `o[k]`); string helpers are cheap aliases |
| Subtype | Works for any mapping subtype implementing the protocol — not dict-only |

## Done when

- [x] Try-all + depth + benches + `.pyi`
