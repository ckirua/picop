# Perf Parity — helpers that are *not* faster from pure Python

**Tier A** measures a `picop` helper called from plain Python against the equivalent
builtin expression (`session.compare` in `bench/`). A ratio below `1.00x` means `picop`
is faster; above it, the builtin is.

Current run (CPython 3.14.7, 3.14.7t, 3.15.0rc2, 3.15.0rc2t on GitHub Actions (Linux x86_64)): **2848** Tier A cases across **53** public modules, **mean 0.78x**. 281 cases (10%) land above `1.02x`, and the only Core / `picop.hot` helper among them is `set_add` — every other loss is a Protocols or Runtime thin wrapper.

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
| `UnicodeWriter` | `cyunicode` | 6.79x | `iadd_build` | interning on the typed Cython path |
| `codec_strict_errors` | `cycodecs` | 5.47x | `codecs.lookup(enc).decode(b, 'strict')` | codec/error-handler bridge for extension authors |
| `interpreter_guard` | `cythread` | 3.71x | `lambda: None` | thin C-API wrapper |
| `mod_import_object` | `cymodule` | 1.95x | `__import__(name)` | module plumbing for embedding code |
| `long_as_ulonglong` | `cylong` | 1.75x | `int(x)` | hands Cython a C integer type |
| `long_as_longlong` | `cylong` | 1.73x | `int(x)` | hands Cython a C integer type |
| `codec_decode` | `cycodecs` | 1.61x | `lambda b, e, err: b.decode(e.decode(), (err or b'strict').decode())` | codec/error-handler bridge for extension authors |
| `long_from_ulonglong` | `cylong` | 1.53x | `int(x)` | hands Cython a C integer type |
| `long_from_longlong` | `cylong` | 1.50x | `int(x)` | hands Cython a C integer type |
| `obj_as_fd` | `cyobject` | 1.40x | `x.fileno()` | last-resort bridge for unknown objects |
| `float_as_double` | `cyfloat` | 1.37x | `float(x)` | hands Cython a C ``double`` |
| `float_from_double` | `cyfloat` | 1.35x | `float(x)` | hands Cython a C ``double`` |
| `codec_encode` | `cycodecs` | 1.35x | `lambda s, e, err: s.encode(e.decode(), (err or b'strict').decode())` | codec/error-handler bridge for extension authors |
| `seq_count` | `cysequence` | 1.24x | `lambda o, v: o.count(v)` | works on any sequence, not just ``list`` |
| `seqiter_new` | `cyiterobject` | 1.20x | `iter(x)` | thin C-API wrapper |
| `num_lshift` | `cynumber` | 1.18x | `a << b` | protocol bridge for unknown number types |
| `long_as_ulong` | `cylong` | 1.12x | `int(x)` | hands Cython a C integer type |
| `long_as_long` | `cylong` | 1.12x | `int(x)` | hands Cython a C integer type |
| `seq_index` | `cysequence` | 1.11x | `lambda o, v: o.index(v)` | works on any sequence, not just ``list`` |
| `long_as_ssize` | `cylong` | 1.11x | `int(x)` | hands Cython a C integer type |
| `obj_type` | `cyobject` | 1.10x | `type(x)` | last-resort bridge for unknown objects |
| `long_from_size` | `cylong` | 1.09x | `int(x)` | hands Cython a C integer type |
| `set_pop` | `cyset` | 1.09x | `s.pop()` | unchecked set mutation |
| `num_as_ssize` | `cynumber` | 1.07x | `operator.index(x)` | protocol bridge for unknown number types |
| `seq_tuple` | `cysequence` | 1.07x | `tuple(x)` | works on any sequence, not just ``list`` |
| `num_long` | `cynumber` | 1.07x | `int(x)` | protocol bridge for unknown number types |
| `long_from_ulong` | `cylong` | 1.06x | `int(x)` | hands Cython a C integer type |
| `long_from_long` | `cylong` | 1.06x | `int(x)` | hands Cython a C integer type |
| `long_from_ssize` | `cylong` | 1.06x | `int(x)` | hands Cython a C integer type |
| `num_float` | `cynumber` | 1.05x | `float(x)` | protocol bridge for unknown number types |
| `set_add` | `cyset` | 1.05x | `s.add(v)` | unchecked set mutation |

*(31 helpers. Ratios are the mean across each helper's Tier A cases; regenerate with `python scripts/perf_parity_report.py --update-doc`.)*

## Slower only on some inputs

These win on most cases and lose on a narrow band. Keep them; know the crossover.

| Helper | Best case | Worst case |
|---|---|---|
| `bytearray_contains` | 0.19x (`3.15: miss`) | 1.05x (`3.14t: hit 1KiB`) |
| `array_ne` | 0.48x (`3.15: eq n=64`) | 1.09x (`3.14t: ne small`) |
| `array_eq` | 0.48x (`3.15: eq n=64`) | 1.08x (`3.14t: ne small`) |
| `func_set_annotations` | 0.55x (`3.15: annotations dict`) | 1.20x (`3.14t: annotations dict`) |
| `dict_eq` | 0.44x (`3.14t: identity`) | 1.24x (`3.14t: eq small`) |
| `hash_buffer` | 0.38x (`3.15: array.array('B') n=6`) | 2.33x (`3.14t: memoryview n=256 (cached)`) |
| `bytes_size` | 0.67x (`3.15t: bytes_size`) | 1.22x (`3.14: bytes_size`) |
| `frozendict_new` | 0.65x (`3.15t: from frozendict`) | 1.08x (`3.15: from dict (4 items)`) |
| `buf_eq` | 0.68x (`3.15: mv↔mv`) | 1.23x (`3.14t: ne`) |
| `list_eq` | 0.55x (`3.15: identity`) | 1.32x (`3.14t: eq small`) |
| `func_get_globals` | 0.76x (`3.15: __globals__`) | 1.08x (`3.14t: __globals__`) |
| `mod_get_filename` | 0.82x (`3.15: json`) | 1.09x (`3.14t: json`) |
| `num_matmul` | 0.75x (`3.14: @`) | 1.04x (`3.14t: @`) |
| `dict_clear` | 0.89x (`3.14t: clear`) | 1.13x (`3.14: clear`) |
| `uintern` | 0.90x (`3.15t: already`) | 1.04x (`3.14t: non-ascii`) |
| `str_endswith` | 0.89x (`3.15t: hit`) | 1.04x (`3.14t: miss`) |
| `mod_new_object` | 0.83x (`3.15: new`) | 1.11x (`3.14t: new`) |
| `list_extend` | 0.93x (`3.15: extend`) | 1.06x (`3.14t: extend`) |
| `set_eq` | 0.78x (`3.15: ne small`) | 1.26x (`3.14t: eq small`) |
| `num_and` | 0.95x (`3.14: bitwise`) | 1.03x (`3.14t: bitwise`) |
| `ansi_wrap` | 0.81x (`3.15: ansi_wrap`) | 1.42x (`3.14t: ansi_wrap`) |
| `num_inplace_sub` | 0.94x (`3.14t: -=`) | 1.02x (`3.14: -=`) |
| `num_inplace_matmul` | 0.90x (`3.14: @=`) | 1.08x (`3.14t: @=`) |
| `obj_iter` | 0.97x (`3.14: iter`) | 1.02x (`3.14t: iter`) |
| `obj_getattr` | 0.97x (`3.15: box.a`) | 1.03x (`3.14t: box.a`) |
| `num_xor` | 0.98x (`3.14: xor`) | 1.02x (`3.14t: xor`) |
| `num_mul` | 0.95x (`3.14: 6*7`) | 1.07x (`3.14t: 6*7`) |
| `codec_ignore_errors` | 0.98x (`3.14: ignore`) | 1.02x (`3.15t: ignore`) |
| `obj_len` | 0.97x (`3.15: dict`) | 1.04x (`3.15t: dict`) |
| `num_inplace_truediv` | 0.98x (`3.15t: /=`) | 1.02x (`3.14t: /=`) |
| `num_pow` | 0.95x (`3.14: 2**10`) | 1.07x (`3.14t: 2**10`) |
| `num_inplace_floordiv` | 0.99x (`3.15t: //=`) | 1.02x (`3.15: //=`) |
| `num_mod` | 0.97x (`3.14: 7%3`) | 1.08x (`3.14t: 7%3`) |
| `call_noargs` | 0.97x (`3.15: zero args`) | 1.07x (`3.14t: zero args`) |
| `num_floordiv` | 0.96x (`3.14: 7//2`) | 1.05x (`3.14t: 7//2`) |
| `num_inplace_or` | 0.99x (`3.15t: |=`) | 1.02x (`3.14t: |=`) |
| `obj_format` | 0.95x (`3.14t: fmt`) | 1.05x (`3.14: fmt`) |
| `seq_inplace_concat` | 0.99x (`3.15: +=`) | 1.03x (`3.14t: +=`) |
| `num_inplace_mul` | 0.98x (`3.15t: *=`) | 1.04x (`3.14t: *=`) |
| `list_set_item` | 0.99x (`3.14: set`) | 1.06x (`3.15t: set`) |
| `ctxvar_reset` | 0.98x (`3.14: set+reset`) | 1.05x (`3.15t: set+reset`) |
| `float_from_cstr` | 1.00x (`3.15: '2.5'`) | 1.04x (`3.14: '2.5'`) |
| `num_inplace_lshift` | 1.00x (`3.15t: <<=`) | 1.05x (`3.15: <<=`) |
| `obj_hasattr` | 0.99x (`3.15: miss`) | 1.06x (`3.14: miss`) |
| `num_add` | 0.99x (`3.14: 3+5`) | 1.06x (`3.14t: 3+5`) |
| `long_from_double` | 1.00x (`3.14: 3.9`) | 1.05x (`3.14t: 3.9`) |
| `long_as_double` | 1.02x (`3.14: 42`) | 1.04x (`3.15: 42`) |
| `obj_str` | 1.01x (`3.14t: 42`) | 1.04x (`3.15: 42`) |
| `obj_getitem` | 1.00x (`3.15: d[a]`) | 1.08x (`3.15t: d[a]`) |
| `set_discard` | 1.00x (`3.15: miss`) | 1.08x (`3.14: miss`) |
| `weakref_new_proxy` | 1.01x (`3.14: new`) | 1.08x (`3.15: new`) |
| `call_twoargs` | 1.02x (`3.15: two args`) | 1.09x (`3.14: two args`) |
| `obj_istrue` | 1.00x (`3.15t: 0`) | 1.07x (`3.14t: 0`) |
| `num_inplace_mod` | 0.97x (`3.14: %=`) | 1.22x (`3.14t: %=`) |
| `set_clear` | 1.02x (`3.15: n=3`) | 1.09x (`3.14: n=3`) |
| `codec_incremental_decoder` | 0.94x (`3.14: utf-8`) | 1.14x (`3.14t: utf-8`) |
| `codec_incremental_encoder` | 0.98x (`3.14: utf-8`) | 1.14x (`3.15t: utf-8`) |
| `seq_slice` | 0.97x (`3.14: mid10`) | 1.17x (`3.15t: mid10`) |
| `set_update` | 1.01x (`3.15: list3`) | 1.12x (`3.15t: list3`) |
| `func_set_closure` | 0.97x (`3.15: none`) | 1.31x (`3.14t: none`) |
| `num_rshift` | 0.99x (`3.15: >>`) | 1.38x (`3.15t: >>`) |
| `complex_real_as_double` | 0.59x (`3.14t: Z.real`) | 1.78x (`3.14t: int 7`) |
| `pickle_buffer_from_object` | 0.15x (`3.15t: pickle.dumps buffer-backed record n=248`) | 3.14x (`3.14t: bytearray n=4096`) |
| `BytesWriter` | 0.02x (`3.14: no hint vs += `) | 6.77x (`3.15: hint 160k vs join`) |

## Why not a runtime warning

A per-call check (`warnings.warn`, a flag, a wrapper) costs more than the helper does —
it is exactly the overhead these helpers exist to avoid. The warning belongs in the
docstring and in this table, which the gate keeps in sync.
