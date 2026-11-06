# Perf Parity — helpers that are *not* faster from pure Python

**Tier A** measures a `picop` helper called from plain Python against the equivalent
builtin expression (`session.compare` in `bench/`). A ratio below `1.00x` means `picop`
is faster; above it, the builtin is.

Current run (CPython 3.15.0rc2 · Linux x86_64 · GIL on · `N=80000 RUNS=5`): **685** Tier A cases across **48** public modules, **mean 0.68x**. 106 cases (15%) land above `1.02x`, and the Core / `picop.hot` helpers among them are `set_add` and `str_len` — every other loss is a Protocols or Runtime thin wrapper.

## The rule

A public helper that loses in **every** measured Tier A case must:

1. carry a `Slower than the plain-Python equivalent …` note in its `.pyi` docstring;
2. appear in the table below.

`python3.14 scripts/ops_inventory_coverage.py --strict` checks both directions: a table
row without the docstring note fails, and a docstring note without a table row fails.
Helpers that lose only on some inputs are in the second table instead.

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
| `long_as_longlong` | `cylong` | 2.41x | `int(x)` | hands Cython a C integer type |
| `mod_import_object` | `cymodule` | 2.18x | `__import__(name)` | module plumbing for embedding code |
| `long_as_ulonglong` | `cylong` | 2.17x | `int(x)` | hands Cython a C integer type |
| `long_from_longlong` | `cylong` | 1.76x | `int(x)` | hands Cython a C integer type |
| `long_from_ulonglong` | `cylong` | 1.72x | `int(x)` | hands Cython a C integer type |
| `num_truediv` | `cynumber` | 1.52x | `a / b` | protocol bridge for unknown number types |
| `float_as_double` | `cyfloat` | 1.37x | `float(x)` | hands Cython a C ``double`` |
| `seqiter_new` | `cyiterobject` | 1.34x | `iter(x)` | thin C-API wrapper |
| `long_as_long` | `cylong` | 1.33x | `int(x)` | hands Cython a C integer type |
| `codec_decode` | `cycodecs` | 1.32x | `lambda b, e, err: b.decode(e.decode(), (err or b'strict').decode())` | codec/error-handler bridge for extension authors |
| `num_index` | `cynumber` | 1.29x | `operator.index(x)` | protocol bridge for unknown number types |
| `num_xor` | `cynumber` | 1.28x | `a ^ b` | protocol bridge for unknown number types |
| `num_as_ssize` | `cynumber` | 1.25x | `operator.index(x)` | protocol bridge for unknown number types |
| `method_new` | `cymethod` | 1.23x | `types.MethodType` | thin C-API wrapper |
| `seq_size` | `cysequence` | 1.22x | `len(x)` | works on any sequence, not just ``list`` |
| `seq_len` | `cysequence` | 1.21x | `len(x)` | works on any sequence, not just ``list`` |
| `obj_size` | `cyobject` | 1.21x | `len(x)` | last-resort bridge for unknown objects |
| `long_as_ssize` | `cylong` | 1.20x | `int(x)` | hands Cython a C integer type |
| `frozenset_new` | `cyset` | 1.20x | `frozenset(it)` | unchecked set mutation |
| `long_as_ulong` | `cylong` | 1.19x | `int(x)` | hands Cython a C integer type |
| `codec_ignore_errors` | `cycodecs` | 1.19x | `codecs.ignore_errors` | codec/error-handler bridge for extension authors |
| `dict_setdefault_ref` | `cydict` | 1.18x | `d.setdefault(key, default)` | unchecked ``PyDict`` mutation on a known dict |
| `num_long` | `cynumber` | 1.18x | `int(x)` | protocol bridge for unknown number types |
| `seq_slice` | `cysequence` | 1.18x | `x[a:b]` | works on any sequence, not just ``list`` |
| `float_from_double` | `cyfloat` | 1.18x | `float(x)` | hands Cython a C ``double`` |
| `obj_istrue` | `cyobject` | 1.16x | `bool(x)` | last-resort bridge for unknown objects |
| `long_from_ulong` | `cylong` | 1.15x | `int(x)` | hands Cython a C integer type |
| `obj_repr` | `cyobject` | 1.15x | `repr(x)` | last-resort bridge for unknown objects |
| `obj_callable` | `cyobject` | 1.14x | `callable(x)` | last-resort bridge for unknown objects |
| `set_add` | `cyset` | 1.14x | `s.add(v)` | unchecked set mutation |
| `num_inplace_floordiv` | `cynumber` | 1.13x | `a //= b` | protocol bridge for unknown number types |
| `codec_encode` | `cycodecs` | 1.13x | `lambda s, e, err: s.encode(e.decode(), (err or b'strict').decode())` | codec/error-handler bridge for extension authors |
| `conv_cstr_to_double` | `cyconversion` | 1.13x | `float(x)` | thin C-API wrapper |
| `type_is_subtype` | `cytype` | 1.12x | `issubclass(a, b)` | thin C-API wrapper |
| `num_mul` | `cynumber` | 1.12x | `a * b` | protocol bridge for unknown number types |
| `long_from_size` | `cylong` | 1.12x | `int(x)` | hands Cython a C integer type |
| `long_from_ssize` | `cylong` | 1.11x | `int(x)` | hands Cython a C integer type |
| `num_abs` | `cynumber` | 1.11x | `abs(x)` | protocol bridge for unknown number types |
| `obj_as_fd` | `cyobject` | 1.11x | `x.fileno()` | last-resort bridge for unknown objects |
| `num_mod` | `cynumber` | 1.11x | `a % b` | protocol bridge for unknown number types |
| `set_pop` | `cyset` | 1.11x | `s.pop()` | unchecked set mutation |
| `long_from_double` | `cylong` | 1.11x | `int(x)` | hands Cython a C integer type |
| `obj_hasattr` | `cyobject` | 1.10x | `hasattr(x, name)` | last-resort bridge for unknown objects |
| `num_neg` | `cynumber` | 1.10x | `-a` | protocol bridge for unknown number types |
| `uintern` | `cyunicode` | 1.09x | `sys.intern(s)` | interning on the typed Cython path |
| `codec_namereplace_errors` | `cycodecs` | 1.09x | `codecs.namereplace_errors` | codec/error-handler bridge for extension authors |
| `obj_issubclass` | `cyobject` | 1.09x | `issubclass(a, b)` | last-resort bridge for unknown objects |
| `num_pos` | `cynumber` | 1.09x | `+a` | protocol bridge for unknown number types |
| `map_len` | `cymapping` | 1.09x | `len(x)` | thin C-API wrapper |
| `num_pow` | `cynumber` | 1.08x | `pow(a, b)` | protocol bridge for unknown number types |
| `num_matmul` | `cynumber` | 1.08x | `a @ b` | protocol bridge for unknown number types |
| `num_invert` | `cynumber` | 1.08x | `~a` | protocol bridge for unknown number types |
| `obj_type` | `cyobject` | 1.08x | `type(x)` | last-resort bridge for unknown objects |
| `obj_len` | `cyobject` | 1.08x | `len(x)` | last-resort bridge for unknown objects |
| `obj_isinstance` | `cyobject` | 1.07x | `isinstance(x, t)` | last-resort bridge for unknown objects |
| `obj_getattr` | `cyobject` | 1.07x | `getattr(x, name)` | last-resort bridge for unknown objects |
| `num_rshift` | `cynumber` | 1.07x | `a >> b` | protocol bridge for unknown number types |
| `num_divmod` | `cynumber` | 1.07x | `divmod(a, b)` | protocol bridge for unknown number types |
| `obj_str` | `cyobject` | 1.06x | `str(x)` | last-resort bridge for unknown objects |
| `codec_backslashreplace_errors` | `cycodecs` | 1.06x | `codecs.backslashreplace_errors` | codec/error-handler bridge for extension authors |
| `bool_from_long` | `cybool` | 1.05x | `bool(x)` | returns the C ``bool`` for a Cython ``int`` |
| `codec_incremental_decoder` | `cycodecs` | 1.05x | `codecs.incremental_decoder(enc)` | codec/error-handler bridge for extension authors |
| `num_and` | `cynumber` | 1.05x | `a & b` | protocol bridge for unknown number types |
| `num_float` | `cynumber` | 1.05x | `float(x)` | protocol bridge for unknown number types |
| `iter_next` | `cyiterator` | 1.05x | `next` | iterator-protocol bridge |
| `num_inplace_and` | `cynumber` | 1.05x | `a &= b` | protocol bridge for unknown number types |
| `set_update` | `cyset` | 1.04x | `s.update(it)` | unchecked set mutation |
| `obj_iter` | `cyobject` | 1.04x | `iter(x)` | last-resort bridge for unknown objects |
| `time_wall` | `cytime` | 1.04x | `time.time` | thin C-API wrapper |
| `set_discard` | `cyset` | 1.04x | `s.discard(v)` | unchecked set mutation |
| `num_inplace_lshift` | `cynumber` | 1.04x | `a <<= b` | protocol bridge for unknown number types |
| `num_or` | `cynumber` | 1.04x | `a | b` | protocol bridge for unknown number types |
| `num_add` | `cynumber` | 1.04x | `a + b` | protocol bridge for unknown number types |
| `num_inplace_sub` | `cynumber` | 1.04x | `a -= b` | protocol bridge for unknown number types |
| `set_clear` | `cyset` | 1.04x | `s.clear()` | unchecked set mutation |
| `str_len` | `cystr` | 1.04x | `len(x)` | ``PyUnicode_GET_LENGTH`` on a known compact ``str`` |
| `long_as_double` | `cylong` | 1.04x | `float(x)` | hands Cython a C integer type |
| `num_inplace_matmul` | `cynumber` | 1.04x | `operator.imatmul` | protocol bridge for unknown number types |
| `seq_inplace_concat` | `cysequence` | 1.03x | `a += b` | works on any sequence, not just ``list`` |
| `time_monotonic` | `cytime` | 1.03x | `time.monotonic` | thin C-API wrapper |
| `long_from_long` | `cylong` | 1.03x | `int(x)` | hands Cython a C integer type |
| `float_from_cstr` | `cyfloat` | 1.03x | `float(x)` | hands Cython a C ``double`` |
| `marshal_dumps` | `cymarshal` | 1.03x | `marshal.dumps` | thin C-API wrapper |
| `obj_setattr_cstr` | `cyobject` | 1.03x | `lambda o, n, v: setattr(o, n.decode(), v) or 0` | last-resort bridge for unknown objects |
| `num_inplace_xor` | `cynumber` | 1.02x | `a ^= b` | protocol bridge for unknown number types |
| `obj_getitem` | `cyobject` | 1.02x | `x[key]` | last-resort bridge for unknown objects |
| `ctxvar_reset` | `cycontextvars` | 1.02x | `var.reset(token)` | context-variable token plumbing |
| `num_lshift` | `cynumber` | 1.02x | `a << b` | protocol bridge for unknown number types |
| `num_inplace_rshift` | `cynumber` | 1.02x | `a >>= b` | protocol bridge for unknown number types |
| `obj_hash` | `cyobject` | 1.02x | `hash(x)` | last-resort bridge for unknown objects |
| `codec_replace_errors` | `cycodecs` | 1.02x | `codecs.replace_errors` | codec/error-handler bridge for extension authors |

*(92 helpers. Ratios are the mean across each helper's Tier A cases; regenerate with `python scripts/perf_parity_report.py --update-doc`.)*

## Slower only on some inputs

These win on most cases and lose on a narrow band. Keep them; know the crossover.

| Helper | Best case | Worst case |
|---|---|---|
| `frozendict_new` | 0.54x (`from frozendict`) | 1.04x (`from dict (4 items)`) |
| `buf_eq` | 0.74x (`mv↔mv`) | 1.15x (`ne`) |
| `str_endswith` | 0.95x (`hit`) | 1.05x (`miss`) |
| `complex_real_as_double` | 0.55x (`Z.real`) | 1.55x (`int 7`) |
| `str_startswith` | 0.98x (`hit`) | 1.12x (`miss`) |

## Why not a runtime warning

A per-call check (`warnings.warn`, a flag, a wrapper) costs more than the helper does —
it is exactly the overhead these helpers exist to avoid. The warning belongs in the
docstring and in this table, which the gate keeps in sync.
