# Perf Parity — helpers that are *not* faster from pure Python

**Tier A** measures a `picop` helper called from plain Python against the equivalent
builtin expression (`session.compare` in `bench/`). A ratio below `1.00x` means `picop`
is faster; above it, the builtin is.

Current run (GitHub Actions Tier A dumps (CPython 3.14.7, 3.14t, 3.15.0rc2, 3.15t); every (helper, case) pair pooled by the median of four runs): **723** Tier A cases across **53** public modules, **mean 0.79x**. 62 cases (9%) land above `1.02x`, and the only Core / `picop.hot` helper among them is `set_add` — every other loss is a Protocols or Runtime thin wrapper.

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
| `codec_strict_errors` | `cycodecs` | 14.59x | `codecs.lookup(enc).decode(b, 'strict')` | codec/error-handler bridge for extension authors |
| `UnicodeWriter` | `cyunicode` | 5.97x | `iadd_build` | interning on the typed Cython path |
| `interpreter_guard` | `cythread` | 4.21x | `lambda: None` | thin C-API wrapper |
| `mod_import_object` | `cymodule` | 1.96x | `__import__(name)` | module plumbing for embedding code |
| `long_as_ulonglong` | `cylong` | 1.84x | `int(x)` | hands Cython a C integer type |
| `long_as_longlong` | `cylong` | 1.78x | `int(x)` | hands Cython a C integer type |
| `codec_decode` | `cycodecs` | 1.60x | `lambda b, e, err: b.decode(e.decode(), (err or b'strict').decode())` | codec/error-handler bridge for extension authors |
| `long_from_ulonglong` | `cylong` | 1.53x | `int(x)` | hands Cython a C integer type |
| `long_from_longlong` | `cylong` | 1.48x | `int(x)` | hands Cython a C integer type |
| `float_as_double` | `cyfloat` | 1.42x | `float(x)` | hands Cython a C ``double`` |
| `codec_encode` | `cycodecs` | 1.42x | `lambda s, e, err: s.encode(e.decode(), (err or b'strict').decode())` | codec/error-handler bridge for extension authors |
| `obj_as_fd` | `cyobject` | 1.41x | `x.fileno()` | last-resort bridge for unknown objects |
| `float_from_double` | `cyfloat` | 1.37x | `float(x)` | hands Cython a C ``double`` |
| `seq_count` | `cysequence` | 1.27x | `lambda o, v: o.count(v)` | works on any sequence, not just ``list`` |
| `seqiter_new` | `cyiterobject` | 1.23x | `iter(x)` | thin C-API wrapper |
| `num_as_ssize` | `cynumber` | 1.13x | `operator.index(x)` | protocol bridge for unknown number types |
| `long_as_ulong` | `cylong` | 1.13x | `int(x)` | hands Cython a C integer type |
| `codec_incremental_decoder` | `cycodecs` | 1.12x | `codecs.incremental_decoder(enc)` | codec/error-handler bridge for extension authors |
| `long_as_ssize` | `cylong` | 1.12x | `int(x)` | hands Cython a C integer type |
| `seq_index` | `cysequence` | 1.12x | `lambda o, v: o.index(v)` | works on any sequence, not just ``list`` |
| `long_as_long` | `cylong` | 1.11x | `int(x)` | hands Cython a C integer type |
| `obj_type` | `cyobject` | 1.09x | `type(x)` | last-resort bridge for unknown objects |
| `set_pop` | `cyset` | 1.09x | `s.pop()` | unchecked set mutation |
| `long_from_ssize` | `cylong` | 1.08x | `int(x)` | hands Cython a C integer type |
| `long_from_size` | `cylong` | 1.07x | `int(x)` | hands Cython a C integer type |
| `set_update` | `cyset` | 1.07x | `s.update(it)` | unchecked set mutation |
| `obj_istrue` | `cyobject` | 1.07x | `bool(x)` | last-resort bridge for unknown objects |
| `long_from_long` | `cylong` | 1.07x | `int(x)` | hands Cython a C integer type |
| `long_from_ulong` | `cylong` | 1.06x | `int(x)` | hands Cython a C integer type |
| `func_set_closure` | `cyfunction` | 1.06x | `lambda fn, c: 0` | function defaults without the Python attribute machinery |
| `num_long` | `cynumber` | 1.06x | `int(x)` | protocol bridge for unknown number types |
| `seq_tuple` | `cysequence` | 1.06x | `tuple(x)` | works on any sequence, not just ``list`` |
| `codec_incremental_encoder` | `cycodecs` | 1.05x | `_inc_enc` | codec/error-handler bridge for extension authors |
| `seq_slice` | `cysequence` | 1.05x | `x[a:b]` | works on any sequence, not just ``list`` |
| `ctxvar_reset` | `cycontextvars` | 1.04x | `var.reset(token)` | context-variable token plumbing |
| `set_add` | `cyset` | 1.04x | `s.add(v)` | unchecked set mutation |
| `num_float` | `cynumber` | 1.04x | `float(x)` | protocol bridge for unknown number types |
| `float_from_cstr` | `cyfloat` | 1.03x | `float(x)` | hands Cython a C ``double`` |
| `num_add` | `cynumber` | 1.03x | `a + b` | protocol bridge for unknown number types |
| `long_from_double` | `cylong` | 1.03x | `int(x)` | hands Cython a C integer type |
| `obj_hasattr` | `cyobject` | 1.03x | `hasattr(x, name)` | last-resort bridge for unknown objects |
| `long_as_double` | `cylong` | 1.03x | `float(x)` | hands Cython a C integer type |
| `obj_str` | `cyobject` | 1.02x | `str(x)` | last-resort bridge for unknown objects |

*(43 helpers. Ratios are the mean across each helper's Tier A cases; regenerate with `python scripts/perf_parity_report.py --update-doc`.)*

## Slower only on some inputs

These win on most cases and lose on a narrow band. Keep them; know the crossover.

| Helper | Best case | Worst case |
|---|---|---|
| `frozendict_new` | 0.64x (`from frozendict`) | 1.05x (`from dict (4 items)`) |
| `buf_eq` | 0.78x (`mv↔mv`) | 1.06x (`ne`) |
| `hash_buffer` | 0.37x (`array.array('B') n=6`) | 2.34x (`memoryview n=256 (cached)`) |
| `str_endswith` | 0.97x (`hit`) | 1.04x (`miss`) |
| `str_startswith` | 0.97x (`hit`) | 1.06x (`miss`) |
| `set_discard` | 1.02x (`hit`) | 1.03x (`miss`) |
| `complex_real_as_double` | 0.63x (`Z.real`) | 1.72x (`int 7`) |
| `pickle_buffer_from_object` | 0.10x (`pickle.dumps buffer-backed record n=248`) | 2.17x (`bytearray n=248`) |
| `BytesWriter` | 0.03x (`no hint vs += `) | 6.00x (`no hint vs join`) |

## Tier B (picop helper vs typed Cython cdef loop)

Only the cases that do **not** beat a typed Cython `cdef` loop are tabulated; they still pay the wrapper cost inside Cython.

| Helper | Module | Ratio | Case |
|---|---|---|---|
| `tb_lineno` | `cytraceback` | 15.74x | default case |
| `buf_eq` | `cybuffer` | 9.95x | ne |
| `buf_eq` | `cybuffer` | 5.72x | bytes↔ba |
| `num_eq` | `cynumber` | 4.24x | int↔float |
| `map_check` | `cymapping` | 3.82x | hit |
| `UnicodeWriter` | `cyunicode` | 3.59x | N=500,000 parts |
| `obj_eq` | `cyobject` | 3.48x | nan is nan |
| `seq_get` | `cysequence` | 3.47x | list[0] |
| `list_get_checked` | `cylist` | 2.68x | index=0 |
| `bytes_bytearray_eq` | `cybytes` | 2.38x | bytes→ba ne |
| `bytearray_eq` | `cybytearray` | 2.26x | ne short |
| `seq_len` | `cysequence` | 2.20x | n=4 |
| `obj_eq` | `cyobject` | 2.12x | int eq |
| `num_eq` | `cynumber` | 2.09x | ne |
| `pickle_buffer_from_object` | `cypicklebuf` | 2.05x | default case |
| `buf_check` | `cybuffer` | 1.99x | hit |
| `long_eq` | `cylong` | 1.86x | ne |
| `num_check` | `cynumber` | 1.64x | hit |
| `bytes_eq` | `cybytes` | 1.62x | ne short |
| `long_eq` | `cylong` | 1.60x | eq big |
| `buf_eq` | `cybuffer` | 1.59x | mv↔mv |
| `tuple_get_checked` | `cytuple` | 1.50x | index=0 |
| `bytes_bytearray_eq` | `cybytes` | 1.45x | bytes→ba eq |
| `bytes_bytearray_eq` | `cybytes` | 1.41x | ba→bytes eq |
| `dict_get` | `cydict` | 1.37x | hit symbol |
| `uintern` | `cyunicode` | 1.33x | already |
| `obj_type` | `cyobject` | 1.29x | str |
| `tuple_eq` | `cytuple` | 1.27x | eq n=64 |
| `list_get` | `cylist` | 1.23x | index=0 |
| `bytearray_eq` | `cybytearray` | 1.21x | eq short |
| `seq_eq` | `cysequence` | 1.21x | tuple↔list eq |
| `str_ge` | `cystr` | 1.21x | ge eq |
| `seq_eq` | `cysequence` | 1.21x | list eq |
| `seq_eq` | `cysequence` | 1.15x | list ne |
| `bytearray_eq` | `cybytearray` | 1.13x | eq 1KiB |
| `dt_date_check` | `cydatetime` | 1.11x | date |
| `warn_ex` | `cywarnings` | 1.10x | default case |
| `call_twoargs` | `cycall` | 1.08x | two args |
| `memoryview_ne` | `cymemoryview` | 1.07x | ne short |
| `bytearray_ne` | `cybytearray` | 1.05x | ne short |
| `str_check` | `cystr` | 1.05x | str |
| `set_eq` | `cyset` | 1.04x | ne small |
| `map_eq` | `cymapping` | 1.04x | dict ne |
| `bytes_check` | `cybytes` | 1.04x | bytes |
| `dict_check` | `cydict` | 1.03x | dict |
| `map_eq` | `cymapping` | 1.03x | dict eq |
| `dict_eq` | `cydict` | 1.03x | eq small |
| `frozendict_check` | `cyfrozendict` | 1.02x | dict miss |
| `set_eq` | `cyset` | 1.02x | eq small |
| `set_contains` | `cyset` | 1.02x | hit |
| `dict_eq` | `cydict` | 1.02x | ne small |
| `tuple_check` | `cytuple` | 1.01x | tuple |
| `bytes_ne` | `cybytes` | 1.01x | ne 1KiB |
| `BytesWriter` | `cybytes` | 1.01x | no hint vs hint (grow path) |
| `list_eq` | `cylist` | 1.01x | eq small |
| `codec_known` | `cycodecs` | 1.01x | utf-8 |
| `obj_len` | `cyobject` | 1.01x | tuple |
| `ansi_bold` | `cyansi` | 1.01x | on |
| `gc_is_enabled` | `cygc` | 1.00x | flag read |
| `bytearray_check` | `cybytearray` | 1.00x | bytearray |
| `str_is` | `cystr` | 1.00x | exact |
| `tuple_check_exact` | `cytuple` | 1.00x | tuple |
| `complex_check` | `cycomplex` | 1.00x | hit |
| `set_check` | `cyset` | 1.00x | set |
| `list_check` | `cylist` | 1.00x | list |
| `frozendict_check` | `cyfrozendict` | 1.00x | hit |
| `bool_check` | `cybool` | 1.00x | hit |
| `memoryview_check` | `cymemoryview` | 1.00x | hit |
| `str_check_exact` | `cystr` | 1.00x | str |
| `str_le` | `cystr` | 1.00x | le eq |
| `tb_depth` | `cytraceback` | 1.00x | default case |
| `slice_check` | `cyslice` | 1.00x | hit |
| `list_eq` | `cylist` | 1.00x | ne small |
| `float_check` | `cyfloat` | 1.00x | hit |
| `tb_lasti` | `cytraceback` | 1.00x | default case |
| `bytes_check_exact` | `cybytes` | 1.00x | bytes |
| `tuple_eq` | `cytuple` | 1.00x | ne small |
| `list_eq` | `cylist` | 1.00x | eq n=64 |
| `dict_contains` | `cydict` | 1.00x | hit |
| `str_lt` | `cystr` | 0.99x | lt |
| `array_check` | `cyarray` | 0.99x | array |
| `deque_eq` | `cydeque` | 0.99x | eq small |
| `frozenset_eq` | `cyset` | 0.99x | ne |
| `deque_eq` | `cydeque` | 0.99x | ne small |
| `memoryview_eq` | `cymemoryview` | 0.99x | eq |
| `long_check` | `cylong` | 0.99x | hit |
| `tuple_get` | `cytuple` | 0.98x | index=2 |
| `slice_eq` | `cyslice` | 0.98x | ne |
| `deque_eq` | `cydeque` | 0.98x | eq n=64 |
| `slice_eq` | `cyslice` | 0.98x | eq |
| `call_onearg` | `cycall` | 0.98x | one arg |
| `memoryview_eq` | `cymemoryview` | 0.97x | ne |
| `range_eq` | `cyrange` | 0.97x | eq |
| `context_eq` | `cycontextvars` | 0.97x | ne values |
| `frozenset_eq` | `cyset` | 0.97x | eq |
| `range_eq` | `cyrange` | 0.96x | ne |
| `tuple_get` | `cytuple` | 0.96x | index=0 |
| `cell_eq` | `cycellobject` | 0.96x | ne |
| `range_eq` | `cyrange` | 0.96x | equiv span |
| `context_eq` | `cycontextvars` | 0.95x | eq values |

*127 of 227 Tier B cases win, median 0.36x (best: `dict_eq` 0.02x, `capsule_check_exact` 0.03x, `seqiter_check` 0.03x, `cell_check` 0.03x, `cell_eq` 0.05x).*

## Why not a runtime warning

A per-call check (`warnings.warn`, a flag, a wrapper) costs more than the helper does —
it is exactly the overhead these helpers exist to avoid. The warning belongs in the
docstring and in this table, which the gate keeps in sync.
