# Perf Parity — helpers that are *not* faster from pure Python

**Tier A** measures a `picop` helper called from plain Python against the equivalent
builtin expression (`session.compare` in `bench/`). A ratio below `1.00x` means `picop`
is faster; above it, the builtin is.

Current run (3.14.7 + 3.15.0rc2 · Linux x86_64 · GIL on · `N=80000 RUNS=5`): **1424** Tier A cases across **53** public modules, **mean 0.72x**. 220 cases (15%) land above `1.02x`, and the only Core / `picop.hot` helper among them is `set_add` — every other loss is a Protocols or Runtime thin wrapper.

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
| `codec_strict_errors` | `cycodecs` | 4.10x | `codecs.lookup(enc).decode(b, 'strict')` | codec/error-handler bridge for extension authors |
| `interpreter_guard` | `cythread` | 3.85x | `lambda: None` | thin C-API wrapper |
| `long_as_longlong` | `cylong` | 2.19x | `int(x)` | hands Cython a C integer type |
| `long_as_ulonglong` | `cylong` | 2.12x | `int(x)` | hands Cython a C integer type |
| `mod_import_object` | `cymodule` | 2.09x | `__import__(name)` | module plumbing for embedding code |
| `long_from_ulonglong` | `cylong` | 1.67x | `int(x)` | hands Cython a C integer type |
| `long_from_longlong` | `cylong` | 1.62x | `int(x)` | hands Cython a C integer type |
| `codec_decode` | `cycodecs` | 1.48x | `lambda b, e, err: b.decode(e.decode(), (err or b'strict').decode())` | codec/error-handler bridge for extension authors |
| `codec_encode` | `cycodecs` | 1.40x | `lambda s, e, err: s.encode(e.decode(), (err or b'strict').decode())` | codec/error-handler bridge for extension authors |
| `obj_type` | `cyobject` | 1.36x | `type(x)` | last-resort bridge for unknown objects |
| `seqiter_new` | `cyiterobject` | 1.31x | `iter(x)` | thin C-API wrapper |
| `float_as_double` | `cyfloat` | 1.29x | `float(x)` | hands Cython a C ``double`` |
| `codec_ignore_errors` | `cycodecs` | 1.24x | `codecs.ignore_errors` | codec/error-handler bridge for extension authors |
| `long_as_ulong` | `cylong` | 1.23x | `int(x)` | hands Cython a C integer type |
| `float_from_double` | `cyfloat` | 1.23x | `float(x)` | hands Cython a C ``double`` |
| `long_as_long` | `cylong` | 1.20x | `int(x)` | hands Cython a C integer type |
| `num_as_ssize` | `cynumber` | 1.19x | `operator.index(x)` | protocol bridge for unknown number types |
| `long_as_ssize` | `cylong` | 1.19x | `int(x)` | hands Cython a C integer type |
| `obj_as_fd` | `cyobject` | 1.17x | `x.fileno()` | last-resort bridge for unknown objects |
| `seq_size` | `cysequence` | 1.16x | `len(x)` | works on any sequence, not just ``list`` |
| `seq_len` | `cysequence` | 1.15x | `len(x)` | works on any sequence, not just ``list`` |
| `weakref_new_proxy` | `cyweakref` | 1.15x | `weakref.proxy(x)` | weak-reference creation from C |
| `long_from_ulong` | `cylong` | 1.14x | `int(x)` | hands Cython a C integer type |
| `map_len` | `cymapping` | 1.14x | `len(x)` | thin C-API wrapper |
| `obj_istrue` | `cyobject` | 1.13x | `bool(x)` | last-resort bridge for unknown objects |
| `obj_len` | `cyobject` | 1.13x | `len(x)` | last-resort bridge for unknown objects |
| `num_inplace_floordiv` | `cynumber` | 1.13x | `a //= b` | protocol bridge for unknown number types |
| `obj_isinstance` | `cyobject` | 1.12x | `isinstance(x, t)` | last-resort bridge for unknown objects |
| `long_from_long` | `cylong` | 1.12x | `int(x)` | hands Cython a C integer type |
| `long_from_ssize` | `cylong` | 1.11x | `int(x)` | hands Cython a C integer type |
| `obj_hasattr` | `cyobject` | 1.11x | `hasattr(x, name)` | last-resort bridge for unknown objects |
| `obj_callable` | `cyobject` | 1.11x | `callable(x)` | last-resort bridge for unknown objects |
| `num_inplace_sub` | `cynumber` | 1.10x | `a -= b` | protocol bridge for unknown number types |
| `obj_issubclass` | `cyobject` | 1.10x | `issubclass(a, b)` | last-resort bridge for unknown objects |
| `obj_repr` | `cyobject` | 1.10x | `repr(x)` | last-resort bridge for unknown objects |
| `long_from_size` | `cylong` | 1.10x | `int(x)` | hands Cython a C integer type |
| `num_xor` | `cynumber` | 1.10x | `a ^ b` | protocol bridge for unknown number types |
| `set_pop` | `cyset` | 1.09x | `s.pop()` | unchecked set mutation |
| `num_mul` | `cynumber` | 1.09x | `a * b` | protocol bridge for unknown number types |
| `num_abs` | `cynumber` | 1.09x | `abs(x)` | protocol bridge for unknown number types |
| `num_long` | `cynumber` | 1.09x | `int(x)` | protocol bridge for unknown number types |
| `num_mod` | `cynumber` | 1.08x | `a % b` | protocol bridge for unknown number types |
| `obj_size` | `cyobject` | 1.08x | `len(x)` | last-resort bridge for unknown objects |
| `num_add` | `cynumber` | 1.08x | `a + b` | protocol bridge for unknown number types |
| `num_pos` | `cynumber` | 1.08x | `+a` | protocol bridge for unknown number types |
| `num_matmul` | `cynumber` | 1.08x | `a @ b` | protocol bridge for unknown number types |
| `num_inplace_lshift` | `cynumber` | 1.07x | `a <<= b` | protocol bridge for unknown number types |
| `long_from_double` | `cylong` | 1.07x | `int(x)` | hands Cython a C integer type |
| `obj_hash` | `cyobject` | 1.07x | `hash(x)` | last-resort bridge for unknown objects |
| `obj_getattr` | `cyobject` | 1.07x | `getattr(x, name)` | last-resort bridge for unknown objects |
| `obj_str` | `cyobject` | 1.07x | `str(x)` | last-resort bridge for unknown objects |
| `obj_getitem` | `cyobject` | 1.07x | `x[key]` | last-resort bridge for unknown objects |
| `num_truediv` | `cynumber` | 1.07x | `a / b` | protocol bridge for unknown number types |
| `num_and` | `cynumber` | 1.07x | `a & b` | protocol bridge for unknown number types |
| `num_rshift` | `cynumber` | 1.07x | `a >> b` | protocol bridge for unknown number types |
| `num_index` | `cynumber` | 1.07x | `operator.index(x)` | protocol bridge for unknown number types |
| `num_floordiv` | `cynumber` | 1.07x | `a // b` | protocol bridge for unknown number types |
| `time_monotonic` | `cytime` | 1.06x | `time.monotonic` | thin C-API wrapper |
| `num_divmod` | `cynumber` | 1.06x | `divmod(a, b)` | protocol bridge for unknown number types |
| `num_inplace_mul` | `cynumber` | 1.06x | `a *= b` | protocol bridge for unknown number types |
| `num_or` | `cynumber` | 1.06x | `a | b` | protocol bridge for unknown number types |
| `obj_iter` | `cyobject` | 1.06x | `iter(x)` | last-resort bridge for unknown objects |
| `set_discard` | `cyset` | 1.06x | `s.discard(v)` | unchecked set mutation |
| `time_wall` | `cytime` | 1.05x | `time.time` | thin C-API wrapper |
| `calliter_new` | `cyiterobject` | 1.05x | `iter(x)` | thin C-API wrapper |
| `num_invert` | `cynumber` | 1.05x | `~a` | protocol bridge for unknown number types |
| `set_add` | `cyset` | 1.05x | `s.add(v)` | unchecked set mutation |
| `num_lshift` | `cynumber` | 1.04x | `a << b` | protocol bridge for unknown number types |
| `num_inplace_rshift` | `cynumber` | 1.04x | `a >>= b` | protocol bridge for unknown number types |
| `num_inplace_and` | `cynumber` | 1.04x | `a &= b` | protocol bridge for unknown number types |
| `num_float` | `cynumber` | 1.04x | `float(x)` | protocol bridge for unknown number types |
| `num_inplace_or` | `cynumber` | 1.04x | `a |= b` | protocol bridge for unknown number types |
| `codec_replace_errors` | `cycodecs` | 1.04x | `codecs.replace_errors` | codec/error-handler bridge for extension authors |
| `num_inplace_mod` | `cynumber` | 1.04x | `a %= b` | protocol bridge for unknown number types |
| `long_as_double` | `cylong` | 1.04x | `float(x)` | hands Cython a C integer type |
| `sentinel_new` | `cysentinel` | 1.04x | `sentinel(name)` | sentinel-singleton bridge for extension authors |
| `num_inplace_truediv` | `cynumber` | 1.03x | `a /= b` | protocol bridge for unknown number types |
| `set_clear` | `cyset` | 1.03x | `s.clear()` | unchecked set mutation |

*(78 helpers. Ratios are the mean across each helper's Tier A cases; regenerate with `python scripts/perf_parity_report.py --update-doc`.)*

## Slower only on some inputs

These win on most cases and lose on a narrow band. Keep them; know the crossover.

| Helper | Best case | Worst case |
|---|---|---|
| `range_eq` | 0.50x (`3.15: identity`) | 1.23x (`3.15: ne step`) |
| `num_sub` | 0.54x (`3.14: 9-4`) | 1.08x (`3.15: 9-4`) |
| `num_eq` | 0.71x (`3.15: int↔float`) | 1.06x (`3.14: int↔float`) |
| `buf_eq` | 0.76x (`3.15: mv↔mv`) | 1.07x (`3.14: ne`) |
| `seq_tuple` | 0.83x (`3.15: list→tuple`) | 1.04x (`3.14: list→tuple`) |
| `list_set_item` | 0.90x (`3.15: set`) | 1.03x (`3.14: set`) |
| `warn_ex` | 0.86x (`3.14: vs warnings.warn stacklevel=2`) | 1.10x (`3.15: vs warnings.warn`) |
| `type_is_subtype` | 0.95x (`3.15: int!<bool`) | 1.04x (`3.14: int!<bool`) |
| `str_endswith` | 0.95x (`3.15: hit`) | 1.05x (`3.14: miss`) |
| `num_inplace_xor` | 0.98x (`3.14: ^=`) | 1.05x (`3.15: ^=`) |
| `codec_backslashreplace_errors` | 1.01x (`3.14: bs`) | 1.02x (`3.15: bs`) |
| `codec_namereplace_errors` | 0.99x (`3.14: name`) | 1.04x (`3.15: name`) |
| `str_len` | 0.98x (`3.15: n=70`) | 1.05x (`3.14: n=70`) |
| `seq_count` | 1.01x (`3.15: count`) | 1.03x (`3.14: count`) |
| `call_noargs` | 0.96x (`3.14: zero args`) | 1.08x (`3.15: zero args`) |
| `str_startswith` | 0.95x (`3.15: hit`) | 1.08x (`3.14: miss`) |
| `float_from_cstr` | 1.02x (`3.15: '2.5'`) | 1.03x (`3.14: '2.5'`) |
| `seq_inplace_concat` | 0.99x (`3.14: +=`) | 1.06x (`3.15: +=`) |
| `marshal_dumps` | 1.02x (`3.15: dict`) | 1.04x (`3.14: dict`) |
| `num_pow` | 1.01x (`3.14: 2**10`) | 1.05x (`3.15: 2**10`) |
| `num_neg` | 1.02x (`3.15: -42`) | 1.05x (`3.14: -42`) |
| `set_update` | 1.02x (`3.15: list3`) | 1.05x (`3.14: list3`) |
| `hash_buffer` | 0.39x (`3.15: array.array('B') n=6`) | 3.08x (`3.15: memoryview n=256 (cached)`) |
| `time_perf_counter` | 1.01x (`3.15: perf`) | 1.08x (`3.14: perf`) |
| `iter_next` | 1.02x (`3.15: count-iter`) | 1.09x (`3.14: count-iter`) |
| `seq_slice` | 0.92x (`3.14: mid10`) | 1.24x (`3.15: mid10`) |
| `complex_real_as_double` | 0.54x (`3.15: Z.real`) | 1.63x (`3.15: int 7`) |
| `bool_from_long` | 1.01x (`3.15: 1→True`) | 1.17x (`3.15: 0→False`) |
| `uintern` | 0.99x (`3.15: short`) | 1.63x (`3.14: already`) |
| `BytesWriter` | 0.02x (`3.14: no hint vs += `) | 3.56x (`3.15: no hint vs join`) |
| `pickle_buffer_from_object` | 0.21x (`3.15: pickle.dumps buffer-backed record n=248`) | 3.56x (`3.15: bytearray n=248`) |
| `UnicodeWriter` | 0.69x (`3.15: no hint vs += `) | 6.41x (`3.15: no hint vs join`) |

## Why not a runtime warning

A per-call check (`warnings.warn`, a flag, a wrapper) costs more than the helper does —
it is exactly the overhead these helpers exist to avoid. The warning belongs in the
docstring and in this table, which the gate keeps in sync.
