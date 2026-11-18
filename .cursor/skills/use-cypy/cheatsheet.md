# picop consumer cheatsheet

Candidate map for the measured-migration workflow in [`SKILL.md`](SKILL.md). These are **not unconditional replacements or speed guarantees**. Prefer examples under `examples/py*.py`.

Default imports: `from picop.hot import …` / `from picop… cimport …`. The former `cypy` namespace and cimport shims were removed in **3.0**.

## Builtin / stdlib replacement map

Use the exact signature from the installed release, not just this table.
Restrict container/string substitutions to known concrete builtin types; subclass
overrides and arbitrary protocols may change behavior. Preserve evaluation order
and evaluate operands once. The full exported-operation index is
[`OPS_INVENTORY.md`](../../../docs/OPS_INVENTORY.md); benchmark labels there locate
candidates, not proof that a caller will be faster.

| Existing expression | Candidate (`picop.hot` unless a module is named) | Eligibility / semantic boundary |
|---|---|---|
| `len(d)`, `len(xs)`, `len(t)`, `len(b)`, `len(s)` | `dict_len`, `list_len`, `tuple_len`, `bytes_len`, `str_len` | Known corresponding type; preserve subclass `__len__` behavior or skip. |
| `k in d` | `dict_contains(d, k)` | Dict, not generic mapping; test key hashing/equality failures. |
| `d.get(k)` | `dict_get(d, k)` | Missing key versus stored `None`, lookup errors, and any explicit default must match the caller; not a replacement for `d[k]` raising `KeyError`. |
| `d[k] = v` | `dict_set(d, k, v)` | Statement-only use; helper returns status `0`, not `None`. Preserve hashing/equality errors. |
| `xs[i]` | `list_get_checked(xs, i)` | Nonnegative integer index; do not assume Python negative-index normalization or slicing. Never substitute unchecked `list_get` without a proven valid index and safe lifetime/concurrency contract. |
| `xs.append(v)` | `list_append(xs, v)` | Discarded return only: `0` versus `None`. |
| `x in s` | `set_contains(s, x)` | Known set; test exceptional inputs, including unhashable keys. |
| `s.add(x)` | `set_add(s, x)` | Discarded return only; check input-specific performance losses before considering this candidate. |
| `needle in b`, `a == b` (bytes) | `bytes_contains(b, needle)`, `bytes_eq(a, b)` | Known bytes operands; integer membership and mixed types are not covered by the bytes-needle mapping. |
| `sub in s`, `a == b` (str) | `str_contains(s, sub)`, `str_eq(a, b)` | Known strings; preserve Unicode and subclass semantics. |
| `struct.pack("<d", x)` / `"<f"` / `"<e"` | `picop.cyfloat.float_pack8` / `float_pack4` / `float_pack2` | Single scalar format only; `little_endian=False` for `>`; compare rounding, overflow, NaN and signed zero. Not native-aligned/mixed records. |
| `struct.unpack("<d", b)[0]` / `"<f"` / `"<e"` | `picop.cyfloat.float_unpack8` / `float_unpack4` / `float_unpack2` | Bytes of exactly 8/4/2 bytes for equivalent accepted inputs. Check trailing bytes and exception types: `struct.error` and picop errors need not match. |
| `x == 0`, `x < 0`, `x > 0` | `picop.cylong.long_is_zero`, `long_is_negative`, `long_is_positive` | Known integers, not arbitrary comparable objects or floats; preserve subclass comparison behavior. |

For each row, use the corresponding module's `bench/<module>_bench.py` for
Python-call evidence or `bench/tier_b/<module>.py` for Cython evidence.
Read [`PERF_PARITY.md`](../../../docs/PERF_PARITY.md) first: **Always slower**
is a default skip for Python; input-specific losses require matching workload
evidence. Absence from a loss table is not evidence of a win.

### Not drop-in substitutions

- `int(x)` / `float(x)` → fixed-width C conversions: range, accepted inputs and
  C return types differ. Consider only when the consumer needs that C contract.
- `t.__dict__` → `type_get_dict(t)`: mapping proxy versus real dictionary;
  the latter is read-only by contract, not a general replacement.
- `int.from_bytes` → integer writer: requires native digit layout and ownership;
  the published writer benchmark uses shift/OR, **not** `int.from_bytes`.
- `struct.Struct` methods, bulk/vectorized operations, I/O, regex, JSON, and
  other stdlib APIs: no blanket mapping here. Keep the existing implementation
  unless an exact documented candidate and representative measurement exist.
- A helper losing in Python does not automatically win through Cython;
  benchmark the actual compiled caller against its original typed expression.

## Core containers / strings (public)

| Module | Example script | Typical symbols |
|--------|----------------|-----------------|
| cytuple | `examples/pytuple.py` | `tuple_check`, `tuple_len`, `tuple_get`, `tuple_pack2`… |
| cybytes | `examples/pybytes.py` | `bytes_len`, `bytes_contains`, `bytes_eq`, `bytes_check` |
| cydict | `examples/pydict.py` | `dict_get`, `dict_set`, `dict_pop`, `dict_len`, `dict_contains` |
| cylist | `examples/pylist.py` | `list_len`, `list_get`, `list_append`, … |
| cyset | `examples/pyset.py` | `set_contains`, `set_add`, `set_len`, … |
| cystr | `examples/pystr.py` | `str_len`, `str_eq`, `str_contains`, `str_startswith` |
| cyunicode | `examples/pyunicode.py` | `uutf8_bytes`, `uintern` (+ cimport `unicode_from_string`) |
| cyansi | `examples/wrap_ansi.py` | `ansi_wrap`, `ansi_fg8`, `ansi_strip` |
| cygc | `examples/pygc.py` | `gc_collect`, `gc_is_enabled` |

## Overlap playbooks (choice, not new APIs)

| Decision | Example |
|----------|---------|
| mapping vs dict | `examples/py_overlap_mapping_vs_dict.py` |
| sequence vs list/tuple | `examples/py_overlap_sequence_vs_list.py` |
| str value ops vs unicode encode/intern | `examples/py_overlap_str_vs_unicode.py` |

Facades: `picop.containers`, `picop.buffers`, `picop.protocols` (discovery); prefer `picop.hot` for micro-opts.

## Other public modules

See `examples/README.md` Orders 14–21, 23–27, 29–36, 39–46, 51, 53 (`pybytearray`, `pyarray`, `pymemoryview`, `pybuffer`, `pysequence`, `pyslice`, `pybool`, `pylong`, `pyfloat`, `pycomplex`, `pynumber`, `pyobject`, `pytype`, `pyfunction`, `pymethod`, `pymodule`, `pyiterator`, `pyiterobject`, `pygenobject`, `pycellobject`, `pydescr`, `pycodecs`, `pydatetime`, `pycontextvars`, `pymapping`, `pymarshal`, `pyfileobject`, `pypycapsule`, `pyweakref`, `pyconversion`, `pytime`).

## Cimport-only (Cython recipes, not Python)

Orders 10–13, 22, 28, 38, 47–50, 52, 63: `cyerr`, `cymem`, `cythread`, `cyatomic`, `cylongintrepr`, `cyref`, `cygetargs`, `cyceval`, `cypystate`, `cypylifecycle`, `cypyport`, `cyversion`, `cylock`.

Use `cimport` from `.pyx` only — see `examples/cython/README.md`. Prefer `from picop… cimport` (not `cypy`).

## Integer construction and typed conversions

The Python `BytesWriter` / `UnicodeWriter` smoke scripts are indexed above.
For the cimport-only `PyLongWriter` digit-buffer API and fixed-width checked
integer conversions, see [`cylong` tracker](../../../docs/modules/021_cylong.md)
and [`examples/cimport_ext/demo.pyx`](../../../examples/cimport_ext/demo.pyx).
The float, type-metadata, and cell examples are in [`examples/README.md`](../../../examples/README.md);
raw-pointer unpack bounds and other trusted-caller caveats are in
[`SAFETY.md`](../../../docs/SAFETY.md).

## n/a

- `cyinstance` — classic-class ABI gone on 3.14; no helpers.
