# Perf Parity — helpers that are *not* faster from pure Python

**Tier A** measures a `picop` helper called from plain Python against the equivalent
builtin expression (`session.compare` in `bench/`). A ratio below `1.00x` means `picop`
is faster; above it, the builtin is.

Current run (6 CI dumps (3.14, 3.14t, 3.15, 3.15t), pooled by the median of the runs): **723** Tier A cases across **53** public modules, **mean 0.79x**. 73 cases (10%) land above `1.02x`, and the only Core / `picop.hot` helper among them is `set_add` — every other loss is a Protocols or Runtime thin wrapper.

## The rule

A public helper that loses in **every** measured Tier A case must:

1. carry a `Slower than the plain-Python equivalent …` note in its `.pyi` docstring;
2. appear in the table below.

`python3.14 scripts/ops_inventory_coverage.py --strict` checks both directions: a table
row without the docstring note fails, and a docstring note without a table row fails.
Helpers that lose only on some inputs are in the second table instead.

`.github/workflows/perf-parity.yml` re-measures the whole matrix (3.14, 3.15, 3.14t,
3.15t) every week and runs `scripts/perf_parity_drift.py` over the four dumps. Tier A
ratios jitter by a few percent between runs, so the job only fails on contradictions
that survive every dump: a documented helper averaging `<= 0.90x` everywhere, or a
helper averaging `>= 1.25x` everywhere that the table is missing. Borderline
movements and the GIL-off cost of each helper are printed for review.

**Never remove them for being slower.** The loss is the cpdef wrapper cost at the Python
boundary, and it disappears inside Cython, where the call is inlined and the arguments
are already typed. Several also return things builtins do not: `set_discard` reports
whether the value was removed, `long_as_longlong` yields a C `long long`, `seq_*` work
on any sequence. Removal is an API break — Core names need a major release, and
Protocols/Runtime names are a documented SDK surface.

## Always slower from pure Python

| Helper | Module | Ratio | Use instead | Why |
|---|---|---|---|---|
| `codec_strict_errors` | `cycodecs` | 15.88x | `codecs.lookup(enc).decode(b, 'strict')` | codec/error-handler bridge for extension authors |
| `UnicodeWriter` | `cyunicode` | 6.18x | `iadd_build` | interning on the typed Cython path |
| `interpreter_guard` | `cythread` | 4.09x | `lambda: None` | thin C-API wrapper |
| `mod_import_object` | `cymodule` | 1.94x | `__import__(name)` | module plumbing for embedding code |
| `long_as_ulonglong` | `cylong` | 1.83x | `int(x)` | hands Cython a C integer type |
| `long_as_longlong` | `cylong` | 1.83x | `int(x)` | hands Cython a C integer type |
| `codec_decode` | `cycodecs` | 1.70x | `lambda b, e, err: b.decode(e.decode(), (err or b'strict').decode())` | codec/error-handler bridge for extension authors |
| `long_from_ulonglong` | `cylong` | 1.59x | `int(x)` | hands Cython a C integer type |
| `long_from_longlong` | `cylong` | 1.58x | `int(x)` | hands Cython a C integer type |
| `float_from_double` | `cyfloat` | 1.46x | `float(x)` | hands Cython a C ``double`` |
| `float_as_double` | `cyfloat` | 1.46x | `float(x)` | hands Cython a C ``double`` |
| `obj_as_fd` | `cyobject` | 1.40x | `x.fileno()` | last-resort bridge for unknown objects |
| `codec_encode` | `cycodecs` | 1.35x | `lambda s, e, err: s.encode(e.decode(), (err or b'strict').decode())` | codec/error-handler bridge for extension authors |
| `seq_count` | `cysequence` | 1.26x | `lambda o, v: o.count(v)` | works on any sequence, not just ``list`` |
| `seqiter_new` | `cyiterobject` | 1.25x | `iter(x)` | thin C-API wrapper |
| `codec_incremental_decoder` | `cycodecs` | 1.19x | `codecs.incremental_decoder(enc)` | codec/error-handler bridge for extension authors |
| `seq_index` | `cysequence` | 1.14x | `lambda o, v: o.index(v)` | works on any sequence, not just ``list`` |
| `long_as_ssize` | `cylong` | 1.13x | `int(x)` | hands Cython a C integer type |
| `long_as_long` | `cylong` | 1.12x | `int(x)` | hands Cython a C integer type |
| `num_as_ssize` | `cynumber` | 1.12x | `operator.index(x)` | protocol bridge for unknown number types |
| `long_as_ulong` | `cylong` | 1.12x | `int(x)` | hands Cython a C integer type |
| `codec_incremental_encoder` | `cycodecs` | 1.12x | `_inc_enc` | codec/error-handler bridge for extension authors |
| `obj_type` | `cyobject` | 1.10x | `type(x)` | last-resort bridge for unknown objects |
| `long_from_ssize` | `cylong` | 1.09x | `int(x)` | hands Cython a C integer type |
| `func_set_closure` | `cyfunction` | 1.09x | `lambda fn, c: 0` | function defaults without the Python attribute machinery |
| `set_pop` | `cyset` | 1.08x | `s.pop()` | unchecked set mutation |
| `seq_slice` | `cysequence` | 1.08x | `x[a:b]` | works on any sequence, not just ``list`` |
| `long_from_size` | `cylong` | 1.08x | `int(x)` | hands Cython a C integer type |
| `set_add` | `cyset` | 1.07x | `s.add(v)` | unchecked set mutation |
| `set_update` | `cyset` | 1.07x | `s.update(it)` | unchecked set mutation |
| `obj_istrue` | `cyobject` | 1.07x | `bool(x)` | last-resort bridge for unknown objects |
| `long_from_long` | `cylong` | 1.07x | `int(x)` | hands Cython a C integer type |
| `long_from_ulong` | `cylong` | 1.06x | `int(x)` | hands Cython a C integer type |
| `num_long` | `cynumber` | 1.06x | `int(x)` | protocol bridge for unknown number types |
| `set_discard` | `cyset` | 1.05x | `s.discard(v)` | unchecked set mutation |
| `obj_hasattr` | `cyobject` | 1.04x | `hasattr(x, name)` | last-resort bridge for unknown objects |
| `seq_tuple` | `cysequence` | 1.04x | `tuple(x)` | works on any sequence, not just ``list`` |
| `long_from_double` | `cylong` | 1.04x | `int(x)` | hands Cython a C integer type |
| `num_inplace_matmul` | `cynumber` | 1.04x | `operator.imatmul` | protocol bridge for unknown number types |
| `num_divmod` | `cynumber` | 1.04x | `divmod(a, b)` | protocol bridge for unknown number types |
| `ctxvar_reset` | `cycontextvars` | 1.04x | `var.reset(token)` | context-variable token plumbing |
| `num_float` | `cynumber` | 1.04x | `float(x)` | protocol bridge for unknown number types |
| `set_clear` | `cyset` | 1.03x | `s.clear()` | unchecked set mutation |
| `obj_getitem` | `cyobject` | 1.03x | `x[key]` | last-resort bridge for unknown objects |
| `num_floordiv` | `cynumber` | 1.03x | `a // b` | protocol bridge for unknown number types |
| `num_mul` | `cynumber` | 1.03x | `a * b` | protocol bridge for unknown number types |
| `num_lshift` | `cynumber` | 1.03x | `a << b` | protocol bridge for unknown number types |
| `num_add` | `cynumber` | 1.03x | `a + b` | protocol bridge for unknown number types |
| `long_as_double` | `cylong` | 1.03x | `float(x)` | hands Cython a C integer type |
| `num_inplace_truediv` | `cynumber` | 1.03x | `a /= b` | protocol bridge for unknown number types |
| `obj_format` | `cyobject` | 1.03x | `format(x, spec)` | last-resort bridge for unknown objects |
| `obj_str` | `cyobject` | 1.03x | `str(x)` | last-resort bridge for unknown objects |
| `num_matmul` | `cynumber` | 1.03x | `a @ b` | protocol bridge for unknown number types |
| `obj_size` | `cyobject` | 1.03x | `len(x)` | last-resort bridge for unknown objects |
| `float_from_cstr` | `cyfloat` | 1.02x | `float(x)` | hands Cython a C ``double`` |

*(55 helpers. Ratios are the mean across each helper's Tier A cases; regenerate with `python scripts/perf_parity_report.py --update-doc`.)*

## Slower only on some inputs

These win on most cases and lose on a narrow band. Keep them; know the crossover.

| Helper | Best case | Worst case |
|---|---|---|
| `hash_buffer` | 0.36x (`array.array('B') n=6`) | 2.25x (`memoryview n=256 (cached)`) |
| `buf_eq` | 0.78x (`bytes↔ba`) | 1.06x (`ne`) |
| `str_endswith` | 0.95x (`hit`) | 1.03x (`miss`) |
| `str_startswith` | 0.96x (`hit`) | 1.03x (`miss`) |
| `complex_real_as_double` | 0.62x (`Z.real`) | 1.70x (`int 7`) |
| `pickle_buffer_from_object` | 0.10x (`pickle.dumps buffer-backed record n=248`) | 1.96x (`bytearray n=248`) |
| `BytesWriter` | 0.03x (`no hint vs += `) | 5.86x (`no hint vs join`) |

## Tier B (picop helper vs typed Cython cdef loop)

Only the cases that do **not** beat a typed Cython `cdef` loop are tabulated; they still pay the wrapper cost inside Cython.

| Helper | Module | Ratio | Case |
|---|---|---|---|
| `buf_eq` | `cybuffer` | 14.18x | ne |
| `tb_lineno` | `cytraceback` | 12.39x | default case |
| `buf_eq` | `cybuffer` | 9.08x | bytes↔ba |
| `num_eq` | `cynumber` | 6.53x | int↔float |
| `UnicodeWriter` | `cyunicode` | 4.69x | N=500,000 parts |
| `obj_eq` | `cyobject` | 3.65x | nan is nan |
| `bytes_bytearray_eq` | `cybytes` | 3.05x | bytes→ba ne |
| `num_eq` | `cynumber` | 2.41x | ne |
| `long_eq` | `cylong` | 2.20x | ne |
| `bytearray_eq` | `cybytearray` | 2.08x | ne short |
| `bytes_bytearray_eq` | `cybytes` | 1.95x | bytes→ba eq |
| `bytes_bytearray_eq` | `cybytes` | 1.86x | ba→bytes eq |
| `bytearray_eq` | `cybytearray` | 1.75x | eq short |
| `buf_check` | `cybuffer` | 1.74x | hit |
| `dict_get` | `cydict` | 1.73x | hit symbol |
| `seq_get` | `cysequence` | 1.68x | list[0] |
| `float_eq` | `cyfloat` | 1.61x | ne |
| `pickle_buffer_from_object` | `cypicklebuf` | 1.60x | default case |
| `float_eq` | `cyfloat` | 1.57x | eq |
| `bytes_eq` | `cybytes` | 1.38x | ne short |
| `list_get` | `cylist` | 1.35x | index=0 |
| `bytearray_ne` | `cybytearray` | 1.34x | ne short |
| `buf_eq` | `cybuffer` | 1.28x | mv↔mv |
| `seq_eq` | `cysequence` | 1.27x | list eq |
| `obj_eq` | `cyobject` | 1.26x | int eq |
| `seq_eq` | `cysequence` | 1.24x | tuple↔list eq |
| `long_eq` | `cylong` | 1.22x | eq big |
| `set_len` | `cyset` | 1.20x | n=4 |
| `seq_eq` | `cysequence` | 1.19x | list ne |
| `list_get_checked` | `cylist` | 1.19x | index=0 |
| `seq_len` | `cysequence` | 1.18x | n=4 |
| `frozendict_check` | `cyfrozendict` | 1.18x | hit |
| `obj_type` | `cyobject` | 1.15x | str |
| `bytearray_len` | `cybytearray` | 1.13x | small |
| `tuple_get_checked` | `cytuple` | 1.13x | index=0 |
| `list_check` | `cylist` | 1.12x | list |
| `memoryview_check` | `cymemoryview` | 1.12x | hit |
| `warn_ex` | `cywarnings` | 1.12x | default case |
| `map_eq` | `cymapping` | 1.11x | dict ne |
| `bytes_check` | `cybytes` | 1.11x | bytes |
| `frozendict_check_exact` | `cyfrozendict` | 1.11x | hit |
| `gc_is_enabled` | `cygc` | 1.10x | flag read |
| `call_twoargs` | `cycall` | 1.10x | two args |
| `dt_date_check` | `cydatetime` | 1.10x | date |
| `unicode_eq` | `cyunicode` | 1.10x | ascii eq |
| `tuple_check_exact` | `cytuple` | 1.10x | tuple |
| `map_eq` | `cymapping` | 1.10x | dict eq |
| `list_eq` | `cylist` | 1.09x | eq small |
| `long_eq` | `cylong` | 1.09x | eq small |
| `codec_known` | `cycodecs` | 1.09x | utf-8 |
| `tuple_eq` | `cytuple` | 1.08x | ne small |
| `list_eq` | `cylist` | 1.07x | ne small |
| `set_eq` | `cyset` | 1.06x | ne small |
| `bytes_len` | `cybytes` | 1.06x | small |
| `str_is` | `cystr` | 1.06x | exact |
| `set_eq` | `cyset` | 1.05x | eq small |
| `anydict_len` | `cyfrozendict` | 1.05x | dict |
| `dict_eq` | `cydict` | 1.05x | eq small |
| `dict_eq` | `cydict` | 1.04x | ne small |
| `bytearray_eq` | `cybytearray` | 1.03x | eq 1KiB |
| `array_len` | `cyarray` | 1.03x | small i |
| `frozenset_eq` | `cyset` | 1.03x | eq |
| `call_onearg` | `cycall` | 1.03x | one arg |
| `long_check` | `cylong` | 1.03x | hit |
| `num_check` | `cynumber` | 1.02x | hit |
| `tuple_get` | `cytuple` | 1.02x | index=0 |
| `frozenset_eq` | `cyset` | 1.02x | ne |
| `list_eq` | `cylist` | 1.02x | eq n=64 |
| `bytearray_check_exact` | `cybytearray` | 1.02x | bytearray |
| `slice_eq` | `cyslice` | 1.02x | ne |
| `tuple_eq` | `cytuple` | 1.01x | eq n=64 |
| `str_ge` | `cystr` | 1.01x | ge eq |
| `anydict_check` | `cyfrozendict` | 1.01x | frozendict |
| `slice_check` | `cyslice` | 1.01x | hit |
| `BytesWriter` | `cybytes` | 1.01x | no hint vs hint (grow path) |
| `str_lt` | `cystr` | 1.01x | lt |
| `int_eq` | `cylong` | 1.00x | eq |
| `tb_lasti` | `cytraceback` | 1.00x | default case |
| `tuple_get` | `cytuple` | 1.00x | index=2 |
| `dict_contains` | `cydict` | 1.00x | hit |
| `unicode_eq` | `cyunicode` | 1.00x | non-ascii eq |
| `deque_eq` | `cydeque` | 1.00x | ne small |
| `str_eq` | `cystr` | 1.00x | eq ascii |
| `bytes_ne` | `cybytes` | 1.00x | ne 1KiB |
| `anydict_check` | `cyfrozendict` | 1.00x | dict |
| `str_le` | `cystr` | 1.00x | le eq |
| `call_noargs` | `cycall` | 1.00x | no args |
| `deque_eq` | `cydeque` | 1.00x | eq n=64 |
| `dict_check` | `cydict` | 1.00x | dict |
| `marshal_dumps` | `cymarshal` | 1.00x | dict |
| `bytes_check_exact` | `cybytes` | 1.00x | bytes |
| `frozendict_check` | `cyfrozendict` | 1.00x | dict miss |
| `str_eq` | `cystr` | 1.00x | equal |
| `ansi_bold` | `cyansi` | 1.00x | on |
| `uutf8_bytes` | `cyunicode` | 0.99x | short |
| `type_check` | `cytype` | 0.99x | hit |
| `deque_eq` | `cydeque` | 0.99x | eq small |
| `tuple_check` | `cytuple` | 0.99x | tuple |
| `slice_eq` | `cyslice` | 0.99x | eq |
| `str_check_exact` | `cystr` | 0.99x | str |
| `bool_check` | `cybool` | 0.98x | hit |
| `context_eq` | `cycontextvars` | 0.98x | ne values |
| `range_eq` | `cyrange` | 0.98x | eq |
| `str_gt` | `cystr` | 0.98x | gt |
| `range_eq` | `cyrange` | 0.97x | equiv span |
| `range_eq` | `cyrange` | 0.96x | ne |
| `array_check` | `cyarray` | 0.96x | array |
| `context_eq` | `cycontextvars` | 0.96x | eq values |
| `bytearray_check` | `cybytearray` | 0.96x | bytearray |
| `anydict_len` | `cyfrozendict` | 0.96x | frozendict |
| `map_check` | `cymapping` | 0.95x | hit |
| `uintern` | `cyunicode` | 0.95x | already |

*115 of 227 Tier B cases win, median 0.31x (best: `bytes_contains` 0.03x, `bytearray_contains` 0.03x, `ansi_bg8` 0.03x, `ansi_fg8` 0.03x, `cell_check` 0.04x).*

## Why not a runtime warning

A per-call check (`warnings.warn`, a flag, a wrapper) costs more than the helper does —
it is exactly the overhead these helpers exist to avoid. The warning belongs in the
docstring and in this table, which the gate keeps in sync.
