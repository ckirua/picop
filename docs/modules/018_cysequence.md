# cysequence

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.sequence` |
| Sources | `src/cypy/cysequence.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Abstract sequence protocol for unknown concrete types. Prefer typed modules (`cylist`/`cytuple`) when the type is known — `sqsize`/`sqlen` lose to `len` from Python.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| sqcheck / sqsize / sqlen | public (cpdef) | `seq_len`/`seq_size` stub-hidden (Tier A `>1.02x` vs `len`) |
| sqeq | public | identity/size + richcompare; preferred `seq_eq` |
| sqconcat / sqrepeat / inplace_* | public | |
| sqget / sqslice / sqset / sqdel / slice mutators | public | |
| sqcount / sqcontains / sqindex | public | |
| sqlist / sqtuple | public | |
| sqfast / sqfast_get / sqfast_items / sqfast_size / sqitem | cimport | Fast macros / pointer |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| sqget (primary) | APPROVED | list **0.93x** / tuple **0.72x** |
| sqcheck / contains / concat / repeat / slice / list / index | APPROVED | 0.37–0.91x |
| sqeq / seq_eq | APPROVED | identity/size + richcompare (issue #23) |
| sqsize / sqlen | APPROVED (API) | **~1.12x** vs `len` — stub-hidden from `.pyi` |
| sqcount | APPROVED (API) | **~1.07x** — stub-hidden from `.pyi` |
| sqtuple | APPROVED | Tier A ~tie (**1.01x**) — remains stubbed |
| sqfast* / sqitem | APPROVED (cimport) | borrowed / unchecked |

## Lifecycle

| Field | Value |
|-------|--------|
| Freeze | **Provisional (Protocols)** after 1.0 — not Core; may evolve under minors |
| Iteration | 1 |
| Last pass | 2026-08-02 — stub-hide Tier A `>1.02x` from `.pyi` |
| Next action | — |

## Decision log

| Function | Hypothesis | Result | Decision | Iteration |
|----------|------------|--------|----------|-----------|
| sqget | Beat `o[i]` | 0.72–0.93x | APPROVED | 1 |
| sqsize | Beat `len` | **1.09x** lose | APPROVED (API) | 1 |
| sqfast* | Hot Cython | macros | APPROVED (cimport) | 1 |
| sqeq | Abstract `==` | identity/size + richcompare | APPROVED | 1 |

## Bench notes

- Harness: [`bench/cysequence_bench.py`](../../bench/cysequence_bench.py) · N=80000 · CPython 3.14.6
- Primary: `sqget` list[0]

## Bench results

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| sqcheck | list / int | 0.37x / 0.44x | pass |
| sqsize / sqlen | list | 1.09x / 1.10x | API keep |
| sqget | list[0] / tuple[2] | 0.93x / 0.72x | pass |
| sqcontains | hit / miss | 0.71x / 0.76x | pass |
| sqindex / sqcount | | 0.91x / 1.05x | pass / API |
| sqslice / concat / repeat | | 0.74–0.90x | pass |
| sqlist / sqtuple | | 0.88x / 1.09x | pass / API |

Summary: 11/15 ≥5% gate · mean **0.83x**.

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cysequence.py`](../../bench/tier_b/cysequence.py) · `cysequence_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| sqget | list[0] | 2.84±0.09ms | 3.00ms | 2.61±0.02ms | **1.09x** | 1.14x | baseline faster |
| sqlen | n=4 | 2.63±0.07ms | 2.74ms | 2.93±0.11ms | **0.90x** | 0.90x | cypy faster |

**Tier B takeaway:** primary `sqget` **1.09x** vs typed Cython baseline (list[0]).



### `*_eq` inventory (Tier A depth)

Harness: [`bench/cyeq_inventory_bench.py`](../../bench/cyeq_inventory_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| seq_eq | list eq | 1.43±0.12ms | 1.76ms | **0.76x** | 0.80x | APPROVED |
| seq_eq | tuple↔list eq | 1.39±0.12ms | 1.69ms | **0.76x** | 0.81x | APPROVED |
| seq_eq | list ne | 1.57±0.06ms | 1.72ms | **0.73x** | 0.75x | APPROVED |
### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| seq_eq | list eq | 15.72±0.08ms | 15.81ms | 10.73±0.04ms | **1.46x** | 1.47x | baseline faster |
| seq_eq | tuple↔list eq | 14.70±0.05ms | 14.77ms | 7.89±0.07ms | **1.86x** | 1.85x | baseline faster |
| seq_eq | list ne | 17.43±0.09ms | 17.55ms | 12.00±0.02ms | **1.45x** | 1.46x | baseline faster |

**Tier B `*_eq` notes:**
- **`seq_eq`:** **Lose 1.45–1.86x** vs typed Cython `==` — abstract sequence path adds type checks. Prefer `list_eq`/`tuple_eq` in cdef loops; Tier A still wins vs Python.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. **Lose 1.45–1.86x** vs typed Cython `==` — abstract sequence path adds type checks. Prefer `list_eq`/`tuple_eq` in cdef loops; Tier A still wins vs Python.

**Tier B:** primary `sqget` **1.10x** vs typed index; `sqlen` **0.90x**.

| Topic | Finding |
|-------|---------|
| Why `sqsize` loses | Abstract `PySequence_Size` → tp_as_sequence indirection; `len` specializes |
| Prefer typed | Use `llen`/`tlen` when type known; prefer `list_eq`/`tuple_eq` over `seq_eq` |
| `seq_eq` | Same semantics as `==` (list≠tuple; identity/size short-circuit then richcompare) |
| `sqfast` | Returns list/tuple as-is; GET_ITEM borrowed — cdef |
| InPlace* | May return new object if type refuses in-place — same as Python `+=` |
| Cheap alias | `sqlen` ≡ `sqsize` (Length/Size) |

## Done when

- [x] Full try-all + depth + benches + `.pyi`
