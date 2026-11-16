# cytype

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.type` |
| Sources | `src/picop/cytype.pxd`, `.pyx`, `.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Type-object checks for Cython. Mutation/alloc helpers stay cimport.

## Inventory

| Symbol | Export | Notes |
|--------|--------|-------|
| type_check / exact / is_subtype | public | |
| type_eq / typeeq | public | identity (`a is b`); soft `typeeq`; not `hot` |
| modified / has_feature / is_gc / generic_* / ready | cimport | type mutation / flags |
| type_get_name / type_get_qualname | public | CPython type metadata |
| type_get_dict | public | real read-only tp_dict; differs from mappingproxy |
| type_get_flags | cimport | raw flags word for batching checks |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| type_check* | APPROVED | **0.38–0.52x** |
| type_is_subtype | APPROVED (API) | **1.04–1.05x** ~tie vs issubclass |
| type_eq / typeeq | APPROVED | identity (issue #36); not `hot` |
| modified / ready / generic / flags | APPROVED (cimport) | type builder surface |
| type_get_name / type_get_qualname / type_get_dict | APPROVED | Metadata accessors; Tier A measured below |
| type_get_flags | APPROVED (cimport) | Raw flags word; cimport-only caller surface |
| PyType_GetModule / PyType_GetModuleState / PyType_GetModuleName | REJECTED | Heap-type-only APIs; builtin types raise TypeError; module state is opaque void*; internal uuid use does not justify public wrapper |
| PyType_GetSlot | REJECTED | Slot-id enum is an unstable API surface |

## Lifecycle

| Field | Value |
|-------|--------|
| Iteration | 1 |
P26-07-22 — `*_eq` inventory Tier A (`cyeq_inventory_bench`)|
| Next action | — |

## Decision log

| Function | Result | Decision | Iteration |
|----------|--------|----------|-----------|
| type_check* | 0.38–0.52x | APPROVED | 1 |
| is_subtype | 1.04–1.05x | APPROVED (API) | 1 |
| type_eq / typeeq | identity (`a is b`); not metaclass `__eq__` | APPROVED | 1 |
| cdef helpers | type mutation | APPROVED (cimport) | 1 |

## Bench notes

- Harness: [`bench/cytype_bench.py`](../../bench/cytype_bench.py) · N=80000

## Bench results

| operation | case | ratio | verdict |
|-----------|------|-------|---------|
| type_check | int / 3 / Sub | 0.50x / 0.38x / 0.46x | pass |
| type_check_exact | int / type | 0.52x / 0.52x | pass |
| type_is_subtype | bool⊂int / int⊄bool | 1.05x / 1.04x | API |
| type_get_name | int | 3.14 **0.65x**, 3.15 **0.76x** | pass |
| type_get_name | Sub | 3.14 **0.54x**, 3.15 **0.43x** | pass |
| type_get_qualname | int | 3.14 **0.66x**, 3.15 **0.58x** | pass |
| type_get_dict | int | 3.14 **0.38x**, 3.15 **0.41x** | pass |
Summary: 3.14 **8/11 pass, mean 0.69x** · 3.15 **9/11 pass, mean 0.62x**; new metadata accessors all meet the ≤1.02 gate.

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cytype.py`](../../bench/tier_b/cytype.py) · `cytype_tb.pyx` · CPython 3.14.6 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | 3.14 ratio | 3.15 ratio | verdict |
|-----------|------|------------|------------|---------|
| type_get_name | — | **0.81x** | **0.75x** | pass |
| type_get_qualname | — | **0.79x** | **0.78x** | pass |
| type_get_flags | — | **0.88x** | **0.92x** | cimport |
| type_get_dict | — | **0.12x** | **0.10x** | pass |
| type_check | hit | **0.96x** | **0.99x** | ~tie |

**Tier B takeaway:** all three public accessors and the cimport flags accessor beat their typed-Cython counterparts on both ABIs; `type_check` was 0.96x/0.99x.



### `*_eq` inventory (Tier A depth)

Harness: [`bench/cyeq_inventory_bench.py`](../../bench/cyeq_inventory_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| type_eq | identity | 0.90±0.03ms | 0.95ms | **0.57x** | 0.58x | APPROVED |
| type_eq | ne | 0.90±0.03ms | 0.93ms | **0.54x** | 0.53x | APPROVED |
### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| type_eq | identity | 2.45±0.01ms | 2.46ms | 5.77±0.03ms | **0.42x** | 0.42x | cypy faster |
| type_eq | ne | 2.44±0.01ms | 2.46ms | 6.15±0.02ms | **0.40x** | 0.40x | cypy faster |

**Tier B `*_eq` notes:**
- **`type_eq`:** **0.40–0.42x** win — pointer/identity compare vs Cython `==`.


### Order 091 depth probes

- `type_get_dict(int)` returns the actual `tp_dict`; `int.__dict__` is a `mappingproxy` over it. The accessor is read-only by contract despite exposing the underlying dictionary.
- A function-local class has a qualified name such as `outer.<locals>.Nested`; `type_get_qualname` preserves this metadata.
- `type_get_flags(int)` returns the raw unsigned `tp_flags` word. The value is implementation/ABI-specific; consumers should test flags, not hard-code a numeric constant.
- `PyType_GetModule*` is rejected because these APIs apply only to heap types created from module specs; builtin types fail, and module state is an opaque `void *`. `PyType_GetSlot` is rejected because its slot-id enum is an unstable surface.
## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. **0.40–0.42x** win — pointer/identity compare vs Cython `==`.

**Tier B:** `type_check` **0.96x / 0.99x** (3.14 / 3.15) — ~parity.

| Topic | Finding |
|-------|---------|
| Check win | Type-flag vs isinstance(type) |
| IsSubtype ~tie | Same C path as issubclass for types |
| Ready/Modified | Must run after manual `tp_*` edits — unsafe from Python |
| HasFeature/IS_GC | Flag macros — cdef |
| Why win | TypeObject slot checks vs isinstance(type) |
| Scale | IsSubtype bool<int ~tie with Python issubclass (1.03x) — clarity keep |
| Safety | Ready/Modified are process-global type mutations — not for hot paths |
| ABI | Heap-type helpers remain; classic class APIs gone (see cyinstance) |
| GCC 14+ | `PyType_*` externs take `type` (not `object`) + cast at wrappers — avoids `PyObject*`/`PyTypeObject*` incompatible-pointer errors when compiling `cytype.pxd` |
| `type_eq` | Identity (`a is b`) — CPython type default; not metaclass `__eq__`; soft `typeeq` (`teq` is `tuple_eq`); measured; leave off `hot` (clarity / not a starter) |
**Order 091 conclusions:** The public name and qualified-name accessors were faster than Python attribute access on both ABIs, while the dictionary accessor especially benefits from returning the real dictionary rather than accessing a mapping proxy. The cimport-only flags accessor keeps raw flag batching available without promising a Python-level API; `int` reports `0x1401502` on both measured runtimes, but consumers must respect ABI-specific flag values and use masks. A function-local class retains `outer.<locals>.Nested` through `type_get_qualname`. The returned type dict is read-only by contract: no caller should mutate it or call `PyType_Modified` as a workaround. These functions neither borrow nor steal caller-owned references; metadata results follow their C API reference contracts, and ordinary CPython refcounting remains under the GIL. Results show no threshold/crossover concern at the measured scale (80,000 Tier A calls and 2,000,000 Tier B loop iterations); ABI comparisons support retaining all three public helpers and the cimport accessor. No new helper fell outside the Tier A ≤1.02 gate. Existing `type_is_subtype` slow/miss paths above 1.02 remain separately documented and were not introduced by this order.


## Done when

- [x] Try-all + depth + benches + `.pyi`

### Stub visibility (2026-08-02)

- Stub-hidden (Tier A `>1.02x`): `type_is_subtype`. Still `cpdef`.

