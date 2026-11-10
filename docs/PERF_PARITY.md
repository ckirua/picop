# Perf Parity — helpers that are *not* faster from pure Python

**Tier A** measures a `picop` helper called from plain Python against the equivalent
builtin expression (`session.compare` in `bench/`). A ratio below `1.00x` means `picop`
is faster; above it, the builtin is.

Current run (CPython 3.15.2 · Linux x86_64 · GIL on · `N=80000 RUNS=5`): **685** Tier A cases across **48** public modules, **mean 0.71x**. 45 cases (7%) land above `1.02x`, and none of them are Core / `picop.hot` helpers — every other loss is a Protocols or Runtime thin wrapper.

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
| `codec_strict_errors` | `cycodecs` | 4.55x | `codecs.lookup(enc).decode(b, 'strict')` | codec/error-handler bridge for extension authors |
| `mod_import_object` | `cymodule` | 1.96x | `__import__(name)` | module plumbing for embedding code |
| `long_as_ulonglong` | `cylong` | 1.77x | `int(x)` | hands Cython a C integer type |
| `long_as_longlong` | `cylong` | 1.77x | `int(x)` | hands Cython a C integer type |
| `long_from_longlong` | `cylong` | 1.57x | `int(x)` | hands Cython a C integer type |
| `codec_decode` | `cycodecs` | 1.54x | `lambda b, e, err: b.decode(e.decode(), (err or b'strict').decode())` | codec/error-handler bridge for extension authors |
| `long_from_ulonglong` | `cylong` | 1.54x | `int(x)` | hands Cython a C integer type |
| `obj_as_fd` | `cyobject` | 1.36x | `x.fileno()` | last-resort bridge for unknown objects |
| `float_as_double` | `cyfloat` | 1.35x | `float(x)` | hands Cython a C ``double`` |
| `float_from_double` | `cyfloat` | 1.34x | `float(x)` | hands Cython a C ``double`` |
| `codec_encode` | `cycodecs` | 1.27x | `lambda s, e, err: s.encode(e.decode(), (err or b'strict').decode())` | codec/error-handler bridge for extension authors |
| `seqiter_new` | `cyiterobject` | 1.26x | `iter(x)` | thin C-API wrapper |
| `seq_count` | `cysequence` | 1.23x | `lambda o, v: o.count(v)` | works on any sequence, not just ``list`` |
| `long_as_ulong` | `cylong` | 1.12x | `int(x)` | hands Cython a C integer type |
| `long_as_long` | `cylong` | 1.11x | `int(x)` | hands Cython a C integer type |
| `long_as_ssize` | `cylong` | 1.11x | `int(x)` | hands Cython a C integer type |
| `num_as_ssize` | `cynumber` | 1.11x | `operator.index(x)` | protocol bridge for unknown number types |
| `seq_slice` | `cysequence` | 1.11x | `x[a:b]` | works on any sequence, not just ``list`` |
| `long_from_size` | `cylong` | 1.09x | `int(x)` | hands Cython a C integer type |
| `set_pop` | `cyset` | 1.09x | `s.pop()` | unchecked set mutation |
| `long_from_long` | `cylong` | 1.09x | `int(x)` | hands Cython a C integer type |
| `long_from_ssize` | `cylong` | 1.08x | `int(x)` | hands Cython a C integer type |
| `obj_type` | `cyobject` | 1.07x | `type(x)` | last-resort bridge for unknown objects |
| `seq_tuple` | `cysequence` | 1.07x | `tuple(x)` | works on any sequence, not just ``list`` |
| `codec_incremental_decoder` | `cycodecs` | 1.07x | `codecs.incremental_decoder(enc)` | codec/error-handler bridge for extension authors |
| `obj_istrue` | `cyobject` | 1.07x | `bool(x)` | last-resort bridge for unknown objects |
| `num_float` | `cynumber` | 1.06x | `float(x)` | protocol bridge for unknown number types |
| `num_mul` | `cynumber` | 1.06x | `a * b` | protocol bridge for unknown number types |
| `codec_incremental_encoder` | `cycodecs` | 1.05x | `_inc_enc` | codec/error-handler bridge for extension authors |
| `num_floordiv` | `cynumber` | 1.04x | `a // b` | protocol bridge for unknown number types |
| `seq_index` | `cysequence` | 1.04x | `lambda o, v: o.index(v)` | works on any sequence, not just ``list`` |
| `num_xor` | `cynumber` | 1.04x | `a ^ b` | protocol bridge for unknown number types |
| `num_inplace_sub` | `cynumber` | 1.03x | `a -= b` | protocol bridge for unknown number types |
| `long_from_ulong` | `cylong` | 1.03x | `int(x)` | hands Cython a C integer type |
| `set_clear` | `cyset` | 1.03x | `s.clear()` | unchecked set mutation |
| `num_or` | `cynumber` | 1.03x | `a | b` | protocol bridge for unknown number types |
| `num_mod` | `cynumber` | 1.03x | `a % b` | protocol bridge for unknown number types |
| `ctxvar_reset` | `cycontextvars` | 1.03x | `var.reset(token)` | context-variable token plumbing |
| `num_inplace_matmul` | `cynumber` | 1.02x | `operator.imatmul` | protocol bridge for unknown number types |
| `num_truediv` | `cynumber` | 1.02x | `a / b` | protocol bridge for unknown number types |
| `obj_str` | `cyobject` | 1.02x | `str(x)` | last-resort bridge for unknown objects |

*(41 helpers. Ratios are the mean across each helper's Tier A cases; regenerate with `python scripts/perf_parity_report.py --update-doc`.)*

## Slower only on some inputs

These win on most cases and lose on a narrow band. Keep them; know the crossover.

| Helper | Best case | Worst case |
|---|---|---|
| `deque_eq` | 0.59x (`identity`) | 1.08x (`eq n=64`) |
| `complex_real_as_double` | 0.64x (`Z.real`) | 1.56x (`int 7`) |
| `hash_buffer` | 0.40x (`array.array('B') n=6`) | 3.03x (`memoryview n=256 (cached)`) |
| `pickle_buffer_from_object` | 0.10x (`pickle.dumps` buffer-backed object) | 2.16x (`memoryview`, bytearray n=6) |

## Why not a runtime warning

A per-call check (`warnings.warn`, a flag, a wrapper) costs more than the helper does —
it is exactly the overhead these helpers exist to avoid. The warning belongs in the
docstring and in this table, which the gate keeps in sync.
