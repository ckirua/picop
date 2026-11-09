# Perf Parity — helpers that are *not* faster from pure Python

**Tier A** measures a `picop` helper called from plain Python against the equivalent
builtin expression (`session.compare` in `bench/`). A ratio below `1.00x` means `picop`
is faster; above it, the builtin is.

Current run (CPython 3.15.0rc2 · Linux x86_64 · GIL on · `N=80000 RUNS=5`): **685** Tier A cases across **48** public modules, **mean 0.68x**. 104 cases (15%) land above `1.02x`, and the Core / `picop.hot` helpers among them are `list_append` and `str_len` — every other loss is a Protocols or Runtime thin wrapper.

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
| `codec_strict_errors` | `cycodecs` | 4.12x | `codecs.lookup(enc).decode(b, 'strict')` | codec/error-handler bridge for extension authors |
| `long_as_longlong` | `cylong` | 2.32x | `int(x)` | hands Cython a C integer type |
| `long_as_ulonglong` | `cylong` | 2.27x | `int(x)` | hands Cython a C integer type |
| `mod_import_object` | `cymodule` | 2.01x | `__import__(name)` | module plumbing for embedding code |
| `long_from_longlong` | `cylong` | 1.78x | `int(x)` | hands Cython a C integer type |
| `long_from_ulonglong` | `cylong` | 1.74x | `int(x)` | hands Cython a C integer type |
| `map_has_key` | `cymapping` | 1.52x | `lambda o, k: k in o` | thin C-API wrapper |
| `map_len` | `cymapping` | 1.48x | `len(x)` | thin C-API wrapper |
| `codec_decode` | `cycodecs` | 1.39x | `lambda b, e, err: b.decode(e.decode(), (err or b'strict').decode())` | codec/error-handler bridge for extension authors |
| `float_as_double` | `cyfloat` | 1.39x | `float(x)` | hands Cython a C ``double`` |
| `num_add` | `cynumber` | 1.30x | `a + b` | protocol bridge for unknown number types |
| `obj_isinstance` | `cyobject` | 1.30x | `isinstance(x, t)` | last-resort bridge for unknown objects |
| `long_as_ssize` | `cylong` | 1.28x | `int(x)` | hands Cython a C integer type |
| `long_as_ulong` | `cylong` | 1.26x | `int(x)` | hands Cython a C integer type |
| `bool_from_long` | `cybool` | 1.26x | `bool(x)` | returns the C ``bool`` for a Cython ``int`` |
| `num_pow` | `cynumber` | 1.24x | `pow(a, b)` | protocol bridge for unknown number types |
| `long_from_long` | `cylong` | 1.23x | `int(x)` | hands Cython a C integer type |
| `long_as_long` | `cylong` | 1.20x | `int(x)` | hands Cython a C integer type |
| `codec_encode` | `cycodecs` | 1.20x | `lambda s, e, err: s.encode(e.decode(), (err or b'strict').decode())` | codec/error-handler bridge for extension authors |
| `codec_ignore_errors` | `cycodecs` | 1.20x | `codecs.ignore_errors` | codec/error-handler bridge for extension authors |
| `float_from_double` | `cyfloat` | 1.20x | `float(x)` | hands Cython a C ``double`` |
| `obj_size` | `cyobject` | 1.19x | `len(x)` | last-resort bridge for unknown objects |
| `num_index` | `cynumber` | 1.19x | `operator.index(x)` | protocol bridge for unknown number types |
| `num_mul` | `cynumber` | 1.19x | `a * b` | protocol bridge for unknown number types |
| `long_from_ulong` | `cylong` | 1.17x | `int(x)` | hands Cython a C integer type |
| `num_long` | `cynumber` | 1.17x | `int(x)` | protocol bridge for unknown number types |
| `obj_getitem` | `cyobject` | 1.16x | `x[key]` | last-resort bridge for unknown objects |
| `seq_slice` | `cysequence` | 1.16x | `x[a:b]` | works on any sequence, not just ``list`` |
| `obj_istrue` | `cyobject` | 1.16x | `bool(x)` | last-resort bridge for unknown objects |
| `bool_false` | `cybool` | 1.16x | `lambda: False` | returns the C ``bool`` for a Cython ``int`` |
| `seq_size` | `cysequence` | 1.15x | `len(x)` | works on any sequence, not just ``list`` |
| `seq_len` | `cysequence` | 1.15x | `len(x)` | works on any sequence, not just ``list`` |
| `obj_callable` | `cyobject` | 1.13x | `callable(x)` | last-resort bridge for unknown objects |
| `obj_getattr` | `cyobject` | 1.13x | `getattr(x, name)` | last-resort bridge for unknown objects |
| `set_clear` | `cyset` | 1.13x | `s.clear()` | unchecked set mutation |
| `num_truediv` | `cynumber` | 1.13x | `a / b` | protocol bridge for unknown number types |
| `long_from_size` | `cylong` | 1.12x | `int(x)` | hands Cython a C integer type |
| `obj_as_fd` | `cyobject` | 1.11x | `x.fileno()` | last-resort bridge for unknown objects |
| `obj_type` | `cyobject` | 1.10x | `type(x)` | last-resort bridge for unknown objects |
| `calliter_new` | `cyiterobject` | 1.09x | `iter(x)` | thin C-API wrapper |
| `set_discard` | `cyset` | 1.09x | `s.discard(v)` | unchecked set mutation |
| `num_matmul` | `cynumber` | 1.09x | `a @ b` | protocol bridge for unknown number types |
| `num_sub` | `cynumber` | 1.09x | `a - b` | protocol bridge for unknown number types |
| `num_pos` | `cynumber` | 1.09x | `+a` | protocol bridge for unknown number types |
| `obj_issubclass` | `cyobject` | 1.08x | `issubclass(a, b)` | last-resort bridge for unknown objects |
| `num_xor` | `cynumber` | 1.08x | `a ^ b` | protocol bridge for unknown number types |
| `type_is_subtype` | `cytype` | 1.08x | `issubclass(a, b)` | thin C-API wrapper |
| `seq_tuple` | `cysequence` | 1.08x | `tuple(x)` | works on any sequence, not just ``list`` |
| `num_invert` | `cynumber` | 1.08x | `~a` | protocol bridge for unknown number types |
| `uintern` | `cyunicode` | 1.07x | `sys.intern(s)` | interning on the typed Cython path |
| `num_inplace_xor` | `cynumber` | 1.07x | `a ^= b` | protocol bridge for unknown number types |
| `num_rshift` | `cynumber` | 1.07x | `a >> b` | protocol bridge for unknown number types |
| `num_or` | `cynumber` | 1.07x | `a | b` | protocol bridge for unknown number types |
| `num_divmod` | `cynumber` | 1.06x | `divmod(a, b)` | protocol bridge for unknown number types |
| `num_lshift` | `cynumber` | 1.06x | `a << b` | protocol bridge for unknown number types |
| `num_inplace_truediv` | `cynumber` | 1.06x | `a /= b` | protocol bridge for unknown number types |
| `long_from_double` | `cylong` | 1.06x | `int(x)` | hands Cython a C integer type |
| `time_wall` | `cytime` | 1.06x | `time.time` | thin C-API wrapper |
| `num_and` | `cynumber` | 1.06x | `a & b` | protocol bridge for unknown number types |
| `seq_inplace_repeat` | `cysequence` | 1.06x | `a *= b` | works on any sequence, not just ``list`` |
| `list_sort` | `cylist` | 1.05x | `lst.sort()` | unchecked ``PyList`` mutation on a known list |
| `long_from_ssize` | `cylong` | 1.05x | `int(x)` | hands Cython a C integer type |
| `marshal_dumps` | `cymarshal` | 1.05x | `marshal.dumps` | thin C-API wrapper |
| `obj_iter` | `cyobject` | 1.05x | `iter(x)` | last-resort bridge for unknown objects |
| `obj_repr` | `cyobject` | 1.05x | `repr(x)` | last-resort bridge for unknown objects |
| `num_inplace_and` | `cynumber` | 1.05x | `a &= b` | protocol bridge for unknown number types |
| `weakref_new_proxy` | `cyweakref` | 1.04x | `weakref.proxy(x)` | weak-reference creation from C |
| `num_inplace_mod` | `cynumber` | 1.04x | `a %= b` | protocol bridge for unknown number types |
| `str_len` | `cystr` | 1.04x | `len(x)` | ``PyUnicode_GET_LENGTH`` on a known compact ``str`` |
| `iter_next` | `cyiterator` | 1.04x | `next` | iterator-protocol bridge |
| `num_inplace_sub` | `cynumber` | 1.04x | `a -= b` | protocol bridge for unknown number types |
| `num_inplace_mul` | `cynumber` | 1.04x | `a *= b` | protocol bridge for unknown number types |
| `set_pop` | `cyset` | 1.04x | `s.pop()` | unchecked set mutation |
| `num_inplace_rshift` | `cynumber` | 1.04x | `a >>= b` | protocol bridge for unknown number types |
| `time_monotonic` | `cytime` | 1.03x | `time.monotonic` | thin C-API wrapper |
| `num_floordiv` | `cynumber` | 1.03x | `a // b` | protocol bridge for unknown number types |
| `codec_replace_errors` | `cycodecs` | 1.03x | `codecs.replace_errors` | codec/error-handler bridge for extension authors |
| `set_update` | `cyset` | 1.03x | `s.update(it)` | unchecked set mutation |
| `codec_incremental_decoder` | `cycodecs` | 1.03x | `codecs.incremental_decoder(enc)` | codec/error-handler bridge for extension authors |
| `time_perf_counter` | `cytime` | 1.03x | `time.perf_counter` | thin C-API wrapper |
| `obj_hash` | `cyobject` | 1.03x | `hash(x)` | last-resort bridge for unknown objects |
| `codec_backslashreplace_errors` | `cycodecs` | 1.03x | `codecs.backslashreplace_errors` | codec/error-handler bridge for extension authors |
| `num_inplace_floordiv` | `cynumber` | 1.03x | `a //= b` | protocol bridge for unknown number types |
| `codec_namereplace_errors` | `cycodecs` | 1.03x | `codecs.namereplace_errors` | codec/error-handler bridge for extension authors |
| `num_float` | `cynumber` | 1.03x | `float(x)` | protocol bridge for unknown number types |
| `list_set_item` | `cylist` | 1.03x | `lst[i] = value` | unchecked ``PyList`` mutation on a known list |
| `codec_incremental_encoder` | `cycodecs` | 1.02x | `_inc_enc` | codec/error-handler bridge for extension authors |
| `obj_str` | `cyobject` | 1.02x | `str(x)` | last-resort bridge for unknown objects |
| `seq_inplace_concat` | `cysequence` | 1.02x | `a += b` | works on any sequence, not just ``list`` |
| `list_append` | `cylist` | 1.02x | `lst.append(x)` | unchecked ``PyList`` mutation on a known list |

*(90 helpers. Ratios are the mean across each helper's Tier A cases; regenerate with `python scripts/perf_parity_report.py --update-doc`.)*

## Slower only on some inputs

These win on most cases and lose on a narrow band. Keep them; know the crossover.

| Helper | Best case | Worst case |
|---|---|---|
| `bytes_ne` | 0.51x (`eq 1KiB`) | 1.32x (`eq same`) |
| `frozendict_new` | 0.53x (`from frozendict`) | 1.03x (`from dict (4 items)`) |
| `str_endswith` | 0.87x (`hit`) | 1.04x (`miss`) |
| `str_startswith` | 0.97x (`hit`) | 1.10x (`miss`) |
| `obj_hasattr` | 0.99x (`hit`) | 1.10x (`miss`) |
| `complex_real_as_double` | 0.56x (`Z.real`) | 1.56x (`int 7`) |

## Why not a runtime warning

A per-call check (`warnings.warn`, a flag, a wrapper) costs more than the helper does —
it is exactly the overhead these helpers exist to avoid. The warning belongs in the
docstring and in this table, which the gate keeps in sync.
