# cylong

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.long` |
| Sources | `src/picop/cylong.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

C↔`int` bridge and exactness checks (`bool` is a long subtype). From Python, `int()`/`float()` often beat boxed helpers — keep as API for Cython call sites.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| long_check / exact | public | Exact rejects `bool` |
| long_eq / int_eq | public | identity + richcompare; preferred `long_eq`; `int_eq` alias |
| long_from_* (long/ulong/ssize/size/ll/ull/double) | public | C constructors |
| long_as_* / masks / double | public | |
| long_as_long_overflow | public | `(value, overflow)` tuple |
| long_from_string / voidptr / as_voidptr / as_ll_overflow | cimport | pointers / out-param |
| FromUnicode | REJECTED | deprecated path in include |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| long_check* | APPROVED | **0.44–0.52x** |
| loeq / long_eq / int_eq | APPROVED | identity + richcompare (issue #25); not on `hot` |
| long_as_long_overflow | APPROVED | **0.73x** |
| long_from_* / long_as_* | APPROVED (API) | **1.14–1.40x** vs `int`/`float` — Cython C bridge |
| string/voidptr/ll_overflow cdef | APPROVED (cimport) | |
| FromUnicode | REJECTED | deprecated |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
P26-07-22 — `*_eq` inventory Tier A (`cyeq_inventory_bench`)|
| Next action | — |

## Decision log

| Function | Result | Decision | Iteration |
|----------|--------|----------|-----------|
| long_check_exact vs bool | 0.52x; False for True | APPROVED | 1 |
| from/as vs int() | 1.14–1.40x lose | APPROVED (API) | 1 |
| overflow tuple | 0.73x | APPROVED | 1 |
| loeq / long_eq / int_eq | identity + richcompare; API symmetry | APPROVED | 1 |

## Bench notes

- Harness: [`bench/cylong_bench.py`](../../bench/cylong_bench.py) · N=80000

## Bench results

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| long_check | int / bool | 0.49x / 0.44x | pass |
| long_check_exact | int / bool | 0.52x / 0.52x | pass |
| long_from_long / ssize / double | | 1.14–1.40x | API |
| long_as_long / ssize / double | | 1.14–1.28x | API |
| long_as_long_overflow | small | 0.73x | pass |

Summary: 5/11 gate · mean **0.93x**.

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cylong.py`](../../bench/tier_b/cylong.py) · `cylong_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| long_check | hit | 2.46±0.01ms | 2.47ms | 2.47±0.00ms | **1.00x** | 1.00x | ~tie |

**Tier B takeaway:** primary `long_check` **1.00x** vs typed Cython baseline (hit).



### `*_eq` inventory (Tier A depth)

Harness: [`bench/cyeq_inventory_bench.py`](../../bench/cyeq_inventory_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| long_eq | eq small | 0.90±0.02ms | 0.94ms | **0.59x** | 0.57x | APPROVED |
| long_eq | ne | 1.15±0.03ms | 1.19ms | **0.78x** | 0.77x | APPROVED |
| long_eq | eq big | 1.24±0.05ms | 1.32ms | **0.72x** | 0.74x | APPROVED |
| int_eq | eq | 0.94±0.06ms | 1.08ms | **0.63x** | 0.69x | APPROVED |
### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| long_eq | eq small | 2.51±0.02ms | 2.53ms | 5.79±0.09ms | **0.43x** | 0.43x | cypy faster |
| long_eq | ne | 5.18±0.04ms | 5.24ms | 5.74±0.02ms | **0.90x** | 0.91x | cypy faster |
| long_eq | eq big | 6.75±0.03ms | 6.78ms | 6.57±0.05ms | **1.03x** | 1.02x | baseline faster |
| int_eq | eq | 2.83±0.71ms | 4.04ms | 5.80±0.05ms | **0.49x** | 0.69x | cypy faster |

**Tier B `*_eq` notes:**
- **`long_eq`:** Small eq **0.43x**; ne **0.90x**; big int ~tie (**1.03x**) — digit compare dominates.
- **`int_eq`:** **0.49x** win (alias of long path).

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. Small eq **0.43x**; ne **0.90x**; big int ~tie (**1.03x**) — digit compare dominates.

**Tier B:** `long_check` **1.00x** vs isinstance — ~parity.

| Topic | Finding |
|-------|---------|
| Check win | Fast type check; exact separates `bool` |
| Why from/as lose | Small-int immortal / `int()` bytecode specializes; helpers still needed for typed C args in Cython |
| Overflow | Tuple wrapper avoids manual out-param from Python |
| Masks | Wrap without exception — document wraparound |
| Why win | Check/Exact beat isinstance; overflow-checked AsLong wins when exception path matters |
| Scale | FromLong/AsLong lose ~1.2x to Python int boxing specializing small ints |
| Safety | `AsLongAndOverflow` sets overflow flag — must read flag, not only return value |
| Subtype | bool is int subclass: Check true, Exact false — matches CPython |
| `long_eq` | Same semantics as `==` (identity then richcompare); `int_eq` thin alias; measured; leave off `hot` (prefer specialized paths / clarity) |


## Done when

- [x] Try-all + depth + benches + `.pyi`

### Stub visibility (2026-08-02)

- Stub-hidden (Tier A `>1.02x`): `long_from_long`, `long_from_ssize`, `long_from_double`, `long_as_long`, `long_as_ssize`, `long_as_double`. Still `cpdef`.

## Order 087 — narrow integer conversions

| Candidate | Status | Mechanism |
|-----------|--------|-----------|
| `PyLong_IsZero` / `IsNegative` / `IsPositive` → `long_is_zero` / `long_is_negative` / `long_is_positive` | APPROVED | Public `cpdef inline` predicates; 3.14 and 3.15 Tier A ratios are below 1.02x, including large integer cases. |
| `PyLong_GetSign` → `long_get_sign` | APPROVED (cimport) | Out-param helper; keeps sign triple available without Python tuple boxing. |
| `PyLong_AsInt32/AsInt64/AsUInt32/AsUInt64` | APPROVED (cimport) | Checked out-param conversions return fixed-width C values; raise on overflow. |
| `PyLong_FromInt32/Int64/UInt32/UInt64` | APPROVED (cimport) | Fixed-width C arguments avoid a generic C-long conversion path. |
| `PyLong_AsInt` | REJECTED | Same 32-bit `int` semantics as `PyLong_AsInt32` on supported LP64/Windows targets; no second wrapper. |
| `PyLong_GetInfo` | REJECTED | One-shot limits dictionary has no hot-path demand; `sys.maxsize` and infinity cover normal queries. |
| `PyLongWriter_Create/Finish/Discard` | APPROVED (cimport), Order 092 | Fixed-capacity native digit construction; ownership and measurements below. There is no writer growth or finish-truncation API. |

### Order 087 Bench results

Tier A ratio = helper / Python comparison (lower is faster).

| Helper | 3.14 small | 3.14 large | 3.15 small | 3.15 large |
|--------|------------|------------|------------|------------|
| `long_is_zero` | 0.58x | 0.58x | 0.60x | 0.49x |
| `long_is_negative` | 0.64x | 0.56x | 0.61x | 0.50x |
| `long_is_positive` | 0.66x | 0.57x | 0.63x | 0.52x |

Tier A scale row (`n=42`): 3.14 ratios 0.62x / 0.65x / 0.62x; 3.15 ratios 0.61x / 0.61x / 0.56x respectively.

### Tier B — narrow conversion

| Helper | ABI | Cython-loop ratio | Decision |
|--------|-----|-------------------|----------|
| `long_check` | 3.14 | 1.00x | tie with the typed Cython `isinstance` loop; already tierB in the inventory |
| `long_check` | 3.15 | 1.00x | tie; no regression from the narrow-conversion additions |
| `long_as_int32` | 3.14 | 4.02x | cimport-only; checked fixed-width result is useful, but slower than `int()` loop |
| `long_as_int32` | 3.15 | 4.70x | cimport-only; checked fixed-width result is useful, but slower than `int()` loop |

## Order 087 Experiment conclusions

The three sign predicates beat their equivalent Python comparisons on both ABIs: measured ratios span 0.49x–0.73x and every Tier A case clears the ≤1.02x gate. Their integer-type checks are part of the CPython contract, not an isinstance-free arbitrary-object test: `bool` is accepted as an `int`, while a non-integer raises `TypeError` (verified on both ABIs). Narrow conversion probes confirm `long_as_int32(2**32)` raises `OverflowError`, while `long_as_uint32(-1)` raises `ValueError` on these CPython builds; bool input converts successfully and non-int input raises `TypeError`. The small-int probe confirms value parity with `long_as_long`; the measured 4.02x/4.70x Tier B ratios show the checked narrow conversion is slower than the `int()` loop, and its value is the range-checked fixed-width C result rather than raw speed. `PyLong_AsInt` duplicates the 32-bit width and semantics; `PyLong_GetInfo` is a one-shot metadata query. The direct digit writer is covered separately by Order 092 below.


## Order 092 — direct-fill integer writer

| Candidate | Status | Mechanism |
|-----------|--------|-----------|
| `PyLong_GetNativeLayout` → `long_native_layout` | APPROVED (cimport) | Returns the process-wide layout pointer; exposes bits per digit, byte size, digit order and byte endianness without allocating a Python tuple. |
| `PyLongWriter_Create` → `long_writer_create` | APPROVED (cimport) | Allocates the final integer's digit storage directly; rejects NULL output pointers before CPython dereferences them and preserves CPython's count/allocation errors. |
| `PyLongWriter_Finish` → `long_writer_finish` | APPROVED (cimport) | Consumes the writer, normalizes high zero digits and returns an owned Python integer; Cython takes the new reference without an extra INCREF. |
| `PyLongWriter_Discard` → `long_writer_discard` | APPROVED (cimport) | Releases an unfinished writer without reading its uninitialized digits; NULL-safe cleanup sibling is included. |

### Order 092 Experiment conclusions

The [public writer contract](https://docs.python.org/3/c-api/long.html#pylongwriter-api)
is available from Python 3.14; 3.15 additionally places it in the Stable ABI.
The [3.14 implementation](https://github.com/python/cpython/blob/3.14/Objects/longobject.c)
uses the newly allocated integer itself as the opaque writer, not an intermediate
buffer: `Create` returns its storage, `Finish` normalizes it and may replace a
compact result with a cached integer, and `Discard` decrefs it. Both close paths
assert unique ownership in debug builds. No existing Python-held integer is
modified and no caller-side unique-ref test is needed.

This is fixed-capacity construction, not a growable writer or a truncating finish.
Every slot must contain a legal digit before finish, including explicit zeros in
unused high slots. A raw handle and its storage become invalid after either close
path; finish consumes even on error. Consumers must not expose the unfinished
object, share its buffer concurrently, or close it twice. Hence all four helpers
and both types are cimport-only; Python exports, stubs and Core remain unchanged.
Native layout metadata is used rather than deprecated private `digit` definitions.

### Order 092 Bench results

Linux x86_64, CPython 3.14.7 / 3.15, five runs, no warmup.
`bench/tier_b/cylong.py`: typed shift/OR accumulation versus native writer fill;
each sample builds `2_000_000 // limbs` integers. Ratio = writer / baseline.
These are whole-loop timings, not per-integer timings; Tier A is n/a because
the raw-pointer API is cimport-only.

| ABI | Limbs | Writer mean±σ | Writer p99 | Baseline mean±σ | Ratio | p99 ratio | Verdict |
|-----|-------|---------------|------------|----------------|-------|-----------|---------|
| 3.14 | 1 | 41.97±0.43ms | 42.43ms | 31.16±1.04ms | 1.35x | 1.29x | baseline faster |
| 3.14 | 32 | 11.00±0.26ms | 11.39ms | 156.07±0.92ms | 0.07x | 0.07x | writer faster |
| 3.14 | 256 | 9.72±0.13ms | 9.85ms | 370.99±7.31ms | 0.03x | 0.03x | writer faster |
| 3.15 | 1 | 46.19±4.87ms | 53.55ms | 30.79±0.31ms | 1.50x | 1.72x | baseline faster |
| 3.15 | 32 | 10.94±0.09ms | 11.08ms | 153.46±16.48ms | 0.07x | 0.06x | writer faster |
| 3.15 | 256 | 9.85±0.13ms | 10.03ms | 348.94±1.91ms | 0.03x | 0.03x | writer faster |

Direct fill avoids repeated Python integer allocations and copying during
shift/OR accumulation. It loses for a single small limb: allocation and finish
overhead exceed the small-integer baseline. Prefer existing scalar constructors
for that case; this API is for native multi-limb producers, not a replacement for
`int.from_bytes` (which was not the benchmark baseline).

Both ABI runs passed positive/negative result parity at every benchmark size,
zero and negative zero, leading-zero normalization, maximum legal digits,
multi-limb assembly, zero-count and NULL-output rejection, NULL discard and
exceptional fill cleanup. Both installed-consumer barrel/direct cimport smoke
runs also passed. The consumer uses all four native layout fields. Local builds
have the standard layout; alternate 15-bit and big-endian builds were not run.

