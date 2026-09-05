# Public `*_eq` Tier B inventory

Measured **cypy `cdef` loop vs typed Cython `==` baseline** with
[`bench/tier_b/cyeq_inventory.py`](../bench/tier_b/cyeq_inventory.py)
(+ generated `cyeq_{containers,buffers,scalars,misc}_tb.pyx`).

**Informational** — does not reopen Tier A gate. N=2_000_000 × runs=5
(heavy shapes N/40) · CPython 3.14 · Linux x86_64.

Companion Tier A: [`EQ_INVENTORY.md`](EQ_INVENTORY.md).

## Summary (39 helpers)

| Class | Count | Helpers (examples) |
|-------|------:|--------------------|
| win | 21 | identity / memcmp / typed scalar paths |
| tie | 5 | thin richcompare wrappers (`set_eq`, `method_eq`, …) |
| mixed | 9 | identity wins + content ~tie/lose |
| lose | 4 | abstract paths (`seq_eq`, `map_eq`, `buf_eq`, …) |

| Helper | Ratios | Class | Note |
|--------|--------|-------|------|
| `list_eq` | 0.23–1.07x | mixed | identity 0.23x; content ~tie/lose |
| `tuple_eq` | 0.26–1.07x | mixed | eq/identity 0.26x; ne ~lose |
| `seq_eq` | 1.45–1.86x | lose | prefer list_eq/tuple_eq in cdef |
| `dict_eq` | 0.11–1.03x | mixed | identity 0.11x; content ~tie |
| `set_eq` | 1.00–1.01x | tie | thin richcompare wrapper |
| `frozenset_eq` | 1.00–1.00x | tie | thin richcompare wrapper |
| `map_eq` | 1.06–1.09x | lose | prefer dict_eq when typed |
| `deque_eq` | 0.41–1.03x | mixed | identity 0.41x; elementwise ~tie |
| `range_eq` | 1.01–1.04x | mixed | slight lose vs Cython == |
| `bytes_eq` | 0.95–1.13x | mixed | eq ~tie; ne 1.13x |
| `bytes_bytearray_eq` | 0.19–0.22x | win | memcmp beats cross-type == |
| `bytearray_eq` | 0.18–0.55x | win | AS_STRING + memcmp |
| `array_eq` | 0.13–0.30x | win | raw buffer compare |
| `memoryview_eq` | 0.39–0.41x | win | typed view compare |
| `buf_eq` | 1.62–5.25x | lose | buffer protocol tax; prefer typed |
| `str_eq` | 1.00–1.61x | mixed | eq ~tie; ne ascii lose |
| `unicode_eq` | 1.00–1.00x | tie | same family as str_eq |
| `bool_eq` | 0.44–0.90x | win | True/identity fast path |
| `float_eq` | 0.51–0.51x | win | typed float compare |
| `long_eq` | 0.43–1.03x | mixed | small win; big ~tie |
| `int_eq` | 0.49–0.49x | win | long alias path |
| `complex_eq` | 0.48–0.48x | win | typed complex compare |
| `num_eq` | 1.03–1.07x | lose | prefer typed long/float |
| `slice_eq` | 0.97–1.01x | tie | thin richcompare |
| `dt_date_eq` | 0.26–0.27x | win | C-level date compare |
| `dt_time_eq` | 0.48–0.48x | win | C-level time compare |
| `dt_datetime_eq` | 0.54–0.54x | win | C-level datetime compare |
| `dt_timedelta_eq` | 0.42–0.42x | win | C-level timedelta compare |
| `type_eq` | 0.40–0.42x | win | pointer/identity |
| `cell_eq` | 0.22–0.91x | win | identity + richcompare |
| `obj_eq` | 0.53–0.97x | win | generic richcompare EQ |
| `func_eq` | 0.41–0.50x | win | identity (is) |
| `method_eq` | 1.00–1.00x | tie | richcompare already tight |
| `mod_eq` | 0.50–0.50x | win | identity |
| `gen_eq` | 0.41–0.50x | win | identity |
| `iter_eq` | 0.41–0.50x | win | identity |
| `weakref_eq` | 0.27–0.95x | win | identity/same-referent |
| `capsule_eq` | 0.41–0.50x | win | identity |
| `context_eq` | 0.42–1.03x | mixed | identity win; values ~tie |

## Mechanism themes

| Theme | Finding |
|-------|---------|
| Identity short-circuit | Helpers that check `a is b` first (**list/dict/deque/cell/func/…**) crush Cython `==` on identity cases (**0.11–0.50x**). |
| Typed memcmp / buffer | `bytearray_eq`, `bytes_bytearray_eq`, `array_eq`, `memoryview_eq` beat Cython `==` in cdef loops. |
| Thin richcompare | `set_eq` / `frozenset_eq` / `method_eq` / `slice_eq` ≈ Cython emit (**~1.00x**). |
| Abstract wrappers | `seq_eq` / `map_eq` / `buf_eq` / `num_eq` lose — prefer typed siblings in cdef code. |
| Tier A still matters | Many ~ties here still **win Tier A** vs Python `==` (call/dispatch overhead). |

## Full table

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| list_eq | eq small | 12.02±0.87ms | 12.95ms | 11.29±0.46ms | **1.07x** | 1.10x | baseline faster |
| list_eq | ne small | 12.04±0.06ms | 12.14ms | 11.96±0.12ms | **1.01x** | 1.00x | ~tie |
| list_eq | identity | 2.52±0.01ms | 2.53ms | 10.74±0.05ms | **0.23x** | 0.23x | cypy faster |
| list_eq | eq n=64 | 1.46±0.02ms | 1.50ms | 1.48±0.04ms | **0.99x** | 0.97x | ~tie |
| tuple_eq | eq small | 2.52±0.02ms | 2.55ms | 9.57±0.07ms | **0.26x** | 0.26x | cypy faster |
| tuple_eq | ne small | 11.93±0.05ms | 11.99ms | 11.17±0.05ms | **1.07x** | 1.06x | baseline faster |
| tuple_eq | identity | 2.55±0.04ms | 2.61ms | 9.61±0.06ms | **0.26x** | 0.27x | cypy faster |
| tuple_eq | eq n=64 | 1.14±0.01ms | 1.16ms | 1.14±0.01ms | **1.00x** | 1.00x | ~tie |
| seq_eq | list eq | 15.72±0.08ms | 15.81ms | 10.73±0.04ms | **1.46x** | 1.47x | baseline faster |
| seq_eq | tuple↔list eq | 14.70±0.05ms | 14.77ms | 7.89±0.07ms | **1.86x** | 1.85x | baseline faster |
| seq_eq | list ne | 17.43±0.09ms | 17.55ms | 12.00±0.02ms | **1.45x** | 1.46x | baseline faster |
| dict_eq | eq small | 23.76±0.85ms | 25.17ms | 23.10±0.19ms | **1.03x** | 1.08x | baseline faster |
| dict_eq | ne small | 26.73±0.03ms | 26.76ms | 26.31±0.06ms | **1.02x** | 1.01x | ~tie |
| dict_eq | identity | 2.51±0.00ms | 2.52ms | 22.96±0.09ms | **0.11x** | 0.11x | cypy faster |
| set_eq | eq small | 28.26±0.02ms | 28.29ms | 28.16±0.04ms | **1.00x** | 1.00x | ~tie |
| set_eq | ne small | 24.04±0.09ms | 24.12ms | 23.80±0.13ms | **1.01x** | 1.01x | ~tie |
| frozenset_eq | eq | 28.80±0.33ms | 29.15ms | 28.80±0.33ms | **1.00x** | 1.00x | ~tie |
| frozenset_eq | ne | 24.10±0.18ms | 24.31ms | 24.06±0.20ms | **1.00x** | 1.00x | ~tie |
| map_eq | dict eq | 24.95±0.27ms | 25.16ms | 22.99±0.07ms | **1.09x** | 1.09x | baseline faster |
| map_eq | dict ne | 28.69±0.10ms | 28.83ms | 27.11±0.57ms | **1.06x** | 1.03x | baseline faster |
| deque_eq | eq small | 100.49±0.48ms | 101.13ms | 100.85±0.28ms | **1.00x** | 1.00x | ~tie |
| deque_eq | ne small | 92.79±0.30ms | 93.13ms | 90.40±0.63ms | **1.03x** | 1.02x | baseline faster |
| deque_eq | identity | 2.61±0.00ms | 2.61ms | 6.31±0.11ms | **0.41x** | 0.41x | cypy faster |
| deque_eq | eq n=64 | 17.56±0.07ms | 17.64ms | 17.57±0.08ms | **1.00x** | 1.00x | ~tie |
| range_eq | eq | 15.98±0.06ms | 16.06ms | 15.33±0.11ms | **1.04x** | 1.04x | baseline faster |
| range_eq | ne | 9.49±0.05ms | 9.56ms | 9.35±0.05ms | **1.01x** | 1.01x | ~tie |
| range_eq | equiv span | 15.95±0.05ms | 16.03ms | 15.29±0.04ms | **1.04x** | 1.04x | baseline faster |
| bytes_eq | eq short | 2.53±0.02ms | 2.56ms | 2.53±0.01ms | **1.00x** | 1.00x | ~tie |
| bytes_eq | ne short | 2.90±0.02ms | 2.93ms | 2.57±0.02ms | **1.13x** | 1.12x | baseline faster |
| bytes_eq | eq 1KiB | 0.06±0.00ms | 0.06ms | 0.07±0.00ms | **0.95x** | 0.87x | cypy faster |
| bytes_bytearray_eq | bytes→ba eq | 3.41±0.02ms | 3.43ms | 18.01±0.09ms | **0.19x** | 0.19x | cypy faster |
| bytes_bytearray_eq | ba→bytes eq | 3.49±0.09ms | 3.62ms | 15.68±0.26ms | **0.22x** | 0.22x | cypy faster |
| bytes_bytearray_eq | bytes→ba ne | 3.80±0.04ms | 3.83ms | 18.60±0.07ms | **0.20x** | 0.20x | cypy faster |
| bytearray_eq | eq short | 2.85±0.00ms | 2.85ms | 16.07±0.13ms | **0.18x** | 0.18x | cypy faster |
| bytearray_eq | ne short | 2.86±0.00ms | 2.86ms | 16.31±0.09ms | **0.18x** | 0.17x | cypy faster |
| bytearray_eq | eq 1KiB | 0.36±0.00ms | 0.36ms | 0.65±0.04ms | **0.55x** | 0.52x | cypy faster |
| array_eq | eq small | 3.24±0.11ms | 3.40ms | 10.80±0.23ms | **0.30x** | 0.30x | cypy faster |
| array_eq | ne small | 3.05±0.02ms | 3.06ms | 12.05±0.05ms | **0.25x** | 0.25x | cypy faster |
| array_eq | eq n=64 | 0.13±0.01ms | 0.14ms | 0.98±0.01ms | **0.13x** | 0.14x | cypy faster |
| memoryview_eq | eq | 11.44±0.01ms | 11.46ms | 29.21±0.04ms | **0.39x** | 0.39x | cypy faster |
| memoryview_eq | ne | 11.81±0.01ms | 11.83ms | 28.55±0.03ms | **0.41x** | 0.41x | cypy faster |
| buf_eq | bytes↔ba | 29.59±0.11ms | 29.73ms | 18.23±0.08ms | **1.62x** | 1.62x | baseline faster |
| buf_eq | mv↔mv | 46.53±0.58ms | 47.46ms | 8.86±0.03ms | **5.25x** | 5.33x | baseline faster |
| buf_eq | ne | 26.81±0.04ms | 26.85ms | 5.78±0.03ms | **4.64x** | 4.62x | baseline faster |
| str_eq | eq ascii | 2.52±0.01ms | 2.54ms | 2.53±0.01ms | **1.00x** | 1.00x | ~tie |
| str_eq | ne ascii | 4.19±0.05ms | 4.26ms | 2.59±0.02ms | **1.61x** | 1.63x | baseline faster |
| unicode_eq | ascii eq | 2.54±0.02ms | 2.58ms | 2.53±0.01ms | **1.00x** | 1.01x | ~tie |
| unicode_eq | non-ascii eq | 2.54±0.03ms | 2.58ms | 2.53±0.01ms | **1.00x** | 1.01x | ~tie |
| bool_eq | True | 2.51±0.01ms | 2.52ms | 5.73±0.04ms | **0.44x** | 0.43x | cypy faster |
| bool_eq | ne | 5.19±0.06ms | 5.29ms | 5.75±0.04ms | **0.90x** | 0.91x | cypy faster |
| float_eq | eq | 2.58±0.04ms | 2.62ms | 5.05±0.04ms | **0.51x** | 0.51x | cypy faster |
| float_eq | ne | 2.56±0.02ms | 2.59ms | 5.02±0.02ms | **0.51x** | 0.51x | cypy faster |
| long_eq | eq small | 2.51±0.02ms | 2.53ms | 5.79±0.09ms | **0.43x** | 0.43x | cypy faster |
| long_eq | ne | 5.18±0.04ms | 5.24ms | 5.74±0.02ms | **0.90x** | 0.91x | cypy faster |
| long_eq | eq big | 6.75±0.03ms | 6.78ms | 6.57±0.05ms | **1.03x** | 1.02x | baseline faster |
| int_eq | eq | 2.83±0.71ms | 4.04ms | 5.80±0.05ms | **0.49x** | 0.69x | cypy faster |
| complex_eq | eq | 3.51±0.02ms | 3.52ms | 7.34±0.03ms | **0.48x** | 0.48x | cypy faster |
| complex_eq | ne | 3.52±0.04ms | 3.57ms | 7.32±0.02ms | **0.48x** | 0.49x | cypy faster |
| num_eq | int↔float | 12.26±0.04ms | 12.29ms | 11.95±0.05ms | **1.03x** | 1.02x | baseline faster |
| num_eq | ne | 6.17±0.04ms | 6.22ms | 5.76±0.02ms | **1.07x** | 1.08x | baseline faster |
| slice_eq | eq | 34.14±0.80ms | 34.99ms | 35.37±0.12ms | **0.97x** | 0.98x | cypy faster |
| slice_eq | ne | 37.90±0.41ms | 38.24ms | 37.46±0.25ms | **1.01x** | 1.01x | ~tie |
| dt_date_eq | eq | 2.40±0.01ms | 2.42ms | 8.76±0.01ms | **0.27x** | 0.28x | cypy faster |
| dt_date_eq | ne | 2.37±0.04ms | 2.42ms | 9.18±0.03ms | **0.26x** | 0.26x | cypy faster |
| dt_time_eq | eq | 3.52±0.01ms | 3.53ms | 7.34±0.06ms | **0.48x** | 0.48x | cypy faster |
| dt_datetime_eq | eq | 3.95±0.03ms | 3.99ms | 7.30±0.01ms | **0.54x** | 0.55x | cypy faster |
| dt_timedelta_eq | eq | 2.47±0.11ms | 2.65ms | 5.86±0.17ms | **0.42x** | 0.43x | cypy faster |
| type_eq | identity | 2.45±0.01ms | 2.46ms | 5.77±0.03ms | **0.42x** | 0.42x | cypy faster |
| type_eq | ne | 2.44±0.01ms | 2.46ms | 6.15±0.02ms | **0.40x** | 0.40x | cypy faster |
| cell_eq | identity | 2.52±0.01ms | 2.53ms | 11.53±0.04ms | **0.22x** | 0.22x | cypy faster |
| cell_eq | same value | 10.20±0.18ms | 10.34ms | 11.15±0.02ms | **0.91x** | 0.92x | cypy faster |
| cell_eq | ne | 10.05±0.06ms | 10.14ms | 11.51±0.02ms | **0.87x** | 0.88x | cypy faster |
| obj_eq | int eq | 3.05±0.02ms | 3.09ms | 5.79±0.05ms | **0.53x** | 0.53x | cypy faster |
| obj_eq | nan is nan | 4.89±0.01ms | 4.91ms | 5.02±0.04ms | **0.97x** | 0.96x | cypy faster |
| func_eq | identity | 2.49±0.01ms | 2.50ms | 4.98±0.01ms | **0.50x** | 0.50x | cypy faster |
| func_eq | ne | 2.50±0.00ms | 2.51ms | 6.18±0.02ms | **0.41x** | 0.40x | cypy faster |
| method_eq | same bound | 6.55±0.01ms | 6.56ms | 6.58±0.05ms | **1.00x** | 0.98x | ~tie |
| method_eq | diff self | 6.57±0.02ms | 6.60ms | 6.55±0.01ms | **1.00x** | 1.01x | ~tie |
| mod_eq | identity | 2.50±0.01ms | 2.51ms | 4.98±0.02ms | **0.50x** | 0.50x | cypy faster |
| gen_eq | identity | 2.50±0.01ms | 2.50ms | 4.99±0.02ms | **0.50x** | 0.50x | cypy faster |
| gen_eq | ne | 2.50±0.00ms | 2.51ms | 6.17±0.02ms | **0.41x** | 0.40x | cypy faster |
| iter_eq | identity | 2.50±0.01ms | 2.50ms | 5.03±0.13ms | **0.50x** | 0.48x | cypy faster |
| iter_eq | ne | 2.51±0.02ms | 2.54ms | 6.17±0.03ms | **0.41x** | 0.41x | cypy faster |
| weakref_eq | same referent | 2.52±0.01ms | 2.53ms | 9.30±0.11ms | **0.27x** | 0.27x | cypy faster |
| weakref_eq | identity | 2.56±0.04ms | 2.62ms | 9.25±0.06ms | **0.28x** | 0.28x | cypy faster |
| weakref_eq | ne referent | 8.42±0.03ms | 8.45ms | 8.86±0.01ms | **0.95x** | 0.95x | cypy faster |
| capsule_eq | identity | 2.49±0.01ms | 2.50ms | 4.99±0.02ms | **0.50x** | 0.50x | cypy faster |
| capsule_eq | ne | 2.50±0.00ms | 2.50ms | 6.18±0.03ms | **0.41x** | 0.40x | cypy faster |
| context_eq | eq values | 41.04±0.53ms | 41.80ms | 40.01±0.36ms | **1.03x** | 1.03x | baseline faster |
| context_eq | ne values | 41.17±0.50ms | 41.89ms | 40.45±0.60ms | **1.02x** | 1.02x | ~tie |
| context_eq | identity | 2.54±0.02ms | 2.57ms | 6.09±0.05ms | **0.42x** | 0.42x | cypy faster |

## Skipped

None — all **39** public ``*_eq`` helpers measured.
