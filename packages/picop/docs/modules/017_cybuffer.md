# cybuffer

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.buffer` |
| Sources | `src/cypy/cybuffer.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Buffer-protocol check/copy for Python, plus cdef wrappers for `Py_buffer*` lifecycle used from Cython.

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| buf_check | cypy | cpdef | public | `PyObject_CheckBuffer` |
| buf_eq | cypy | cpdef | public | buffer-protocol content eq; soft `buffer_eq`; not `bytes_bytearray_eq` (concrete bytes/ba) |
| buf_copy_data | cypy | cpdef | public | `PyObject_CopyData` |
| buf_get / buf_release | cypy | cdef | cimport | GetBuffer / Release |
| buf_get_pointer / size_from_format | cypy | cdef | cimport | |
| buf_to/from_contiguous / is_contiguous | cypy | cdef | cimport | |
| buf_fill_* | cypy | cdef | cimport | FillInfo / strides |
| PyBUF_* flags | C-API | tried | — | use `cpython.buffer` directly |
| PyObject_Format | C-API | REJECTED | — | deprecated in include → `cpython.object` |
| PyObject_CopyToObject | C-API | tried | — | covered by CopyData path; not wrapped (duplicate-ish) |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| buf_check | APPROVED | primary **0.20x** |
| buf_eq | APPROVED | mirrors `memoryview_eq` over abstract buffers |
| buf_copy_data | APPROVED | **0.53x** |
| buf_* pointer helpers | APPROVED (cimport) | `Py_buffer*` lifetime |
| PyObject_Format | REJECTED | include says cimport from object |
| PyBUF_* re-export | REJECTED | prefer `cpython.buffer` constants |

## Lifecycle

| Field | Value |
|-------|--------|
| Freeze | **1.0 Core** — public + documented cimport; see COVERAGE § 1.0 freeze |
| Iteration | 1 |
P26-07-22 — `*_eq` inventory Tier A (`cyeq_inventory_bench`)|
| Next action | — |

## Decision log

| Function | Hypothesis | Bench | Result | Decision | Iteration |
|----------|------------|-------|--------|----------|-----------|
| buf_check | Beat try/memoryview | hit/miss | **0.11–0.21x** | APPROVED | 1 |
| buf_copy_data | Beat mv slice assign | 8B | **0.53x** | APPROVED | 1 |
| GetBuffer family | Needed in Cython | ABI | cdef | APPROVED (cimport) | 1 |

## Bench notes

- Harness: [`bench/cybuffer_bench.py`](../../bench/cybuffer_bench.py) · N=80000 · CPython 3.14.6

## Bench results

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| buf_check | bytearray | 0.91±0.03ms | 0.95ms | 0.20x | 0.21x | pass |
| buf_check | bytes | 0.95±0.07ms | 1.06ms | 0.21x | 0.23x | pass |
| buf_check | list | 0.92±0.04ms | 0.98ms | 0.12x | 0.12x | pass |
| buf_check | int | 0.88±0.01ms | 0.90ms | 0.11x | 0.12x | pass |
| buf_copy_data | ba←ba 8 | 7.33±0.09ms | 7.46ms | 0.53x | 0.54x | pass |

Summary: 5/5 faster · mean **0.23x**.

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cybuffer.py`](../../bench/tier_b/cybuffer.py) · `cybuffer_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| buf_check | hit | 2.91±0.01ms | 2.91ms | 2.93±0.15ms | **0.99x** | 0.93x | ~tie |

**Tier B takeaway:** primary `buf_check` **0.99x** vs typed Cython baseline (hit).



### `*_eq` inventory (Tier A depth)

Harness: [`bench/cyeq_inventory_bench.py`](../../bench/cyeq_inventory_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| buf_eq | bytes↔ba | 1.79±0.02ms | 1.85ms | **0.81x** | 0.79x | APPROVED |
| buf_eq | mv↔mv | 3.10±0.03ms | 3.16ms | **1.14x** | 1.10x | LOSE (prefer typed helper) |
| buf_eq | ne | 1.70±0.02ms | 1.75ms | **0.92x** | 0.88x | APPROVED |
### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| buf_eq | bytes↔ba | 29.59±0.11ms | 29.73ms | 18.23±0.08ms | **1.62x** | 1.62x | baseline faster |
| buf_eq | mv↔mv | 46.53±0.58ms | 47.46ms | 8.86±0.03ms | **5.25x** | 5.33x | baseline faster |
| buf_eq | ne | 26.81±0.04ms | 26.85ms | 5.78±0.03ms | **4.64x** | 4.62x | baseline faster |

**Tier B `*_eq` notes:**
- **`buf_eq`:** **Lose 1.62–5.25x** (worst mv↔mv) — buffer-protocol acquisition dominates; prefer typed `memoryview_eq` / `bytes_eq` in cdef loops.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. **Lose 1.62–5.25x** (worst mv↔mv) — buffer-protocol acquisition dominates; prefer typed `memoryview_eq` / `bytes_eq` in cdef loops.

**`buf_eq` depth:** bytes↔bytearray **0.81x** (win); memoryview↔memoryview **1.14x** (lose vs `==` — prefer `memoryview_eq` for typed views).



**Tier B:** `buf_check` **1.00x** vs isinstance — ~parity.

| Topic | Finding |
|-------|---------|
| Why `buf_check` wins | `PyObject_CheckBuffer` is a type-slot peek; baseline `try: memoryview` allocates/raises |
| `buf_get`/`release` | Must pair; releasing twice / use-after-release is UB — cdef |
| Flags | Not re-exported; cimport `PyBUF_*` from `cpython.buffer` |
| CopyToObject | Left unwrapped — overlapping with CopyData + rare |
| Why win | `PyObject_CheckBuffer` is a thin slot test vs catching BufferError in Python |
| Scale | Copy path ~0.52x on small bytearray; large copies dominated by memcpy either way |
| Safety | `buf_copy_data` requires writable destination; overlapping regions undefined |
| ABI | Buffer protocol stable on 3.14; view getters stay cdef where pointers escape |


## Done when

- [x] Inventory + try-all + depth + benches + `.pyi`
