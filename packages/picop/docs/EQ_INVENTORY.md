# Public `*_eq` Tier A inventory

Measured vs Python ``==`` with [`bench/cyeq_inventory_bench.py`](../bench/cyeq_inventory_bench.py)
(+ dedicated harnesses for bytes/deque/range/context/misc).

**Gate:** mean ratio ≤ 0.95 (≥5% win). N=80_000 × runs=11 · CPython 3.14.

## Summary (inventory pass)

| Helper | Ratios | Gate |
|--------|--------|------|
| `list_eq` | 0.54–0.86x | pass |
| `tuple_eq` | 0.53–0.85x | pass |
| `seq_eq` | 0.73–0.76x | pass |
| `dict_eq` | 0.39–0.78x | pass |
| `set_eq` / `frozenset_eq` | 0.78–0.80x | pass |
| `map_eq` | 0.79–0.82x | pass |
| `bytearray_eq` | 0.49–0.62x | pass |
| `array_eq` | 0.40–0.60x | pass |
| `memoryview_eq` | 0.47–0.50x | pass |
| `buf_eq` | 0.81–0.92x; **mv↔mv 1.14x lose** | mixed |
| `bool_eq` / `float_eq` / `long_eq` / `int_eq` / `complex_eq` / `num_eq` | 0.59–0.78x | pass |
| `dt_*_eq` | 0.57–0.65x | pass |
| `slice_eq` | 0.82–0.84x | pass |
| `type_eq` / `cell_eq` / `unicode_eq` | 0.51–0.72x | pass |

Earlier dedicated passes: `bytes_eq`, `bytes_bytearray_eq`, `deque_eq`, `range_eq`,
`context_eq`, identity misc — see module trackers / [`EQ_RUNTIME.md`](EQ_RUNTIME.md).

## Explicit lose

- **`buf_eq` memoryview↔memoryview (1.14x):** keep helper for abstract buffer pairs;
  prefer **`memoryview_eq`** when both sides are typed views.

## Tier B

See [`EQ_INVENTORY_TIERB.md`](EQ_INVENTORY_TIERB.md) for cdef-vs-Cython ratios.
