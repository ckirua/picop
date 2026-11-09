# Perf Parity — helpers that are *not* faster from pure Python

**Tier A** measures a `picop` helper called from plain Python against the equivalent
builtin expression (`session.compare` in `bench/`). A ratio below `1.00x` means `picop`
is faster; above it, the builtin is.

Current run (CPython 3.15.0rc2 · Linux x86_64 · GIL on · `N=80000 RUNS=5`): **685** Tier A cases across **48** public modules, **mean 0.68x**. 95 cases (14%) land above `1.02x`, and the only Core / `picop.hot` helper among them is `str_len` — every other loss is a Protocols or Runtime thin wrapper.

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
| `codec_strict_errors` | `cycodecs` | 4.13x | `codecs.lookup(enc).decode(b, 'strict')` | codec/error-handler bridge for extension authors |
| `long_as_longlong` | `cylong` | 2.31x | `int(x)` | hands Cython a C integer type |
| `long_as_ulonglong` | `cylong` | 2.22x | `int(x)` | hands Cython a C integer type |
| `mod_import_object` | `cymodule` | 2.13x | `__import__(name)` | module plumbing for embedding code |
| `long_from_ulonglong` | `cylong` | 1.78x | `int(x)` | hands Cython a C integer type |
| `long_from_longlong` | `cylong` | 1.74x | `int(x)` | hands Cython a C integer type |
| `num_divmod` | `cynumber` | 1.71x | `divmod(a, b)` | protocol bridge for unknown number types |
| `long_from_double` | `cylong` | 1.36x | `int(x)` | hands Cython a C integer type |
| `conv_cstr_to_double` | `cyconversion` | 1.34x | `float(x)` | thin C-API wrapper |
| `float_as_double` | `cyfloat` | 1.34x | `float(x)` | hands Cython a C ``double`` |
| `long_from_size` | `cylong` | 1.32x | `int(x)` | hands Cython a C integer type |
| `codec_decode` | `cycodecs` | 1.31x | `lambda b, e, err: b.decode(e.decode(), (err or b'strict').decode())` | codec/error-handler bridge for extension authors |
| `num_inplace_xor` | `cynumber` | 1.28x | `a ^= b` | protocol bridge for unknown number types |
| `obj_isinstance` | `cyobject` | 1.26x | `isinstance(x, t)` | last-resort bridge for unknown objects |
| `long_as_ulong` | `cylong` | 1.23x | `int(x)` | hands Cython a C integer type |
| `num_as_ssize` | `cynumber` | 1.22x | `operator.index(x)` | protocol bridge for unknown number types |
| `obj_hash` | `cyobject` | 1.22x | `hash(x)` | last-resort bridge for unknown objects |
| `float_from_double` | `cyfloat` | 1.22x | `float(x)` | hands Cython a C ``double`` |
| `codec_ignore_errors` | `cycodecs` | 1.19x | `codecs.ignore_errors` | codec/error-handler bridge for extension authors |
| `obj_hasattr` | `cyobject` | 1.19x | `hasattr(x, name)` | last-resort bridge for unknown objects |
| `seq_slice` | `cysequence` | 1.17x | `x[a:b]` | works on any sequence, not just ``list`` |
| `seq_len` | `cysequence` | 1.16x | `len(x)` | works on any sequence, not just ``list`` |
| `obj_size` | `cyobject` | 1.15x | `len(x)` | last-resort bridge for unknown objects |
| `long_as_ssize` | `cylong` | 1.15x | `int(x)` | hands Cython a C integer type |
| `long_from_long` | `cylong` | 1.15x | `int(x)` | hands Cython a C integer type |
| `seq_size` | `cysequence` | 1.15x | `len(x)` | works on any sequence, not just ``list`` |
| `num_mod` | `cynumber` | 1.14x | `a % b` | protocol bridge for unknown number types |
| `obj_str` | `cyobject` | 1.13x | `str(x)` | last-resort bridge for unknown objects |
| `codec_encode` | `cycodecs` | 1.12x | `lambda s, e, err: s.encode(e.decode(), (err or b'strict').decode())` | codec/error-handler bridge for extension authors |
| `long_from_ulong` | `cylong` | 1.12x | `int(x)` | hands Cython a C integer type |
| `num_long` | `cynumber` | 1.12x | `int(x)` | protocol bridge for unknown number types |
| `seq_tuple` | `cysequence` | 1.11x | `tuple(x)` | works on any sequence, not just ``list`` |
| `set_pop` | `cyset` | 1.11x | `s.pop()` | unchecked set mutation |
| `num_mul` | `cynumber` | 1.11x | `a * b` | protocol bridge for unknown number types |
| `num_neg` | `cynumber` | 1.10x | `-a` | protocol bridge for unknown number types |
| `long_from_ssize` | `cylong` | 1.10x | `int(x)` | hands Cython a C integer type |
| `num_or` | `cynumber` | 1.10x | `a | b` | protocol bridge for unknown number types |
| `num_sub` | `cynumber` | 1.10x | `a - b` | protocol bridge for unknown number types |
| `num_xor` | `cynumber` | 1.09x | `a ^ b` | protocol bridge for unknown number types |
| `bool_from_long` | `cybool` | 1.09x | `bool(x)` | returns the C ``bool`` for a Cython ``int`` |
| `obj_as_fd` | `cyobject` | 1.09x | `x.fileno()` | last-resort bridge for unknown objects |
| `str_len` | `cystr` | 1.09x | `len(x)` | ``PyUnicode_GET_LENGTH`` on a known compact ``str`` |
| `uintern` | `cyunicode` | 1.09x | `sys.intern(s)` | interning on the typed Cython path |
| `num_truediv` | `cynumber` | 1.08x | `a / b` | protocol bridge for unknown number types |
| `num_matmul` | `cynumber` | 1.08x | `a @ b` | protocol bridge for unknown number types |
| `num_invert` | `cynumber` | 1.08x | `~a` | protocol bridge for unknown number types |
| `num_pow` | `cynumber` | 1.08x | `pow(a, b)` | protocol bridge for unknown number types |
| `num_and` | `cynumber` | 1.08x | `a & b` | protocol bridge for unknown number types |
| `num_pos` | `cynumber` | 1.07x | `+a` | protocol bridge for unknown number types |
| `num_abs` | `cynumber` | 1.07x | `abs(x)` | protocol bridge for unknown number types |
| `num_index` | `cynumber` | 1.07x | `operator.index(x)` | protocol bridge for unknown number types |
| `call_twoargs` | `cycall` | 1.07x | `py_twoargs` | thin C-API wrapper |
| `time_wall` | `cytime` | 1.07x | `time.time` | thin C-API wrapper |
| `obj_issubclass` | `cyobject` | 1.07x | `issubclass(a, b)` | last-resort bridge for unknown objects |
| `set_clear` | `cyset` | 1.06x | `s.clear()` | unchecked set mutation |
| `long_as_double` | `cylong` | 1.06x | `float(x)` | hands Cython a C integer type |
| `num_rshift` | `cynumber` | 1.06x | `a >> b` | protocol bridge for unknown number types |
| `num_inplace_and` | `cynumber` | 1.06x | `a &= b` | protocol bridge for unknown number types |
| `num_inplace_truediv` | `cynumber` | 1.06x | `a /= b` | protocol bridge for unknown number types |
| `num_floordiv` | `cynumber` | 1.06x | `a // b` | protocol bridge for unknown number types |
| `list_sort` | `cylist` | 1.05x | `lst.sort()` | unchecked ``PyList`` mutation on a known list |
| `obj_getattr` | `cyobject` | 1.05x | `getattr(x, name)` | last-resort bridge for unknown objects |
| `num_float` | `cynumber` | 1.05x | `float(x)` | protocol bridge for unknown number types |
| `num_inplace_mul` | `cynumber` | 1.04x | `a *= b` | protocol bridge for unknown number types |
| `float_from_cstr` | `cyfloat` | 1.04x | `float(x)` | hands Cython a C ``double`` |
| `num_add` | `cynumber` | 1.04x | `a + b` | protocol bridge for unknown number types |
| `ctxvar_reset` | `cycontextvars` | 1.04x | `var.reset(token)` | context-variable token plumbing |
| `obj_repr` | `cyobject` | 1.04x | `repr(x)` | last-resort bridge for unknown objects |
| `num_inplace_sub` | `cynumber` | 1.04x | `a -= b` | protocol bridge for unknown number types |
| `marshal_dumps` | `cymarshal` | 1.03x | `marshal.dumps` | thin C-API wrapper |
| `num_inplace_mod` | `cynumber` | 1.03x | `a %= b` | protocol bridge for unknown number types |
| `map_len` | `cymapping` | 1.03x | `len(x)` | thin C-API wrapper |
| `obj_iter` | `cyobject` | 1.03x | `iter(x)` | last-resort bridge for unknown objects |
| `num_inplace_rshift` | `cynumber` | 1.03x | `a >>= b` | protocol bridge for unknown number types |
| `iter_next` | `cyiterator` | 1.03x | `next` | iterator-protocol bridge |
| `calliter_new` | `cyiterobject` | 1.03x | `iter(x)` | thin C-API wrapper |
| `seq_inplace_concat` | `cysequence` | 1.03x | `a += b` | works on any sequence, not just ``list`` |
| `num_inplace_or` | `cynumber` | 1.03x | `a |= b` | protocol bridge for unknown number types |
| `time_perf_counter` | `cytime` | 1.02x | `time.perf_counter` | thin C-API wrapper |
| `num_inplace_lshift` | `cynumber` | 1.02x | `a <<= b` | protocol bridge for unknown number types |

*(80 helpers. Ratios are the mean across each helper's Tier A cases; regenerate with `python scripts/perf_parity_report.py --update-doc`.)*

## Slower only on some inputs

These win on most cases and lose on a narrow band. Keep them; know the crossover.

| Helper | Best case | Worst case |
|---|---|---|
| `frozendict_new` | 0.52x (`from frozendict`) | 1.03x (`from dict (4 items)`) |
| `str_contains` | 0.61x (`hit short`) | 1.06x (`miss short`) |
| `uutf8_bytes` | 0.94x (`short`) | 1.02x (`n=64`) |
| `str_startswith` | 0.93x (`hit`) | 1.14x (`miss`) |
| `str_endswith` | 0.92x (`hit`) | 1.17x (`miss`) |
| `obj_callable` | 0.97x (`int`) | 1.12x (`len`) |
| `complex_real_as_double` | 0.56x (`Z.real`) | 1.54x (`int 7`) |
| `obj_istrue` | 1.00x (`dict`) | 1.30x (`0`) |

## Why not a runtime warning

A per-call check (`warnings.warn`, a flag, a wrapper) costs more than the helper does —
it is exactly the overhead these helpers exist to avoid. The warning belongs in the
docstring and in this table, which the gate keeps in sync.
