# picop consumer cheatsheet

Candidate map for the measured-migration workflow in [`SKILL.md`](SKILL.md). These are **not unconditional replacements or speed guarantees**. Prefer examples under `examples/py*.py`.

Default imports: `from picop.hot import …` / `from picop… cimport …`. The former `cypy` namespace and cimport shims were removed in **3.0**.

# Complete replacement map

Use the [authoritative source-derived catalog](catalog.md) for exact per-symbol
access mode, decision, equivalent expression/use, semantic contract and
benchmark evidence. This cheatsheet intentionally has no competing helper
decision table: coverage is not a speed guarantee, and only consumer-specific
measurement can establish a KEEP.

Follow the skill's [measured-migration workflow](SKILL.md#workflow-retain-only-measured-wins):
profile, prove equivalence, benchmark the real call site repeatedly, require a
repeatable ≥5% improvement beyond noise, then run consumer tests. Report KEEP,
SKIP or UNMEASURED.

## Module and example discovery

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
