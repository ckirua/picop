# Examples

How to read this index:

| Tier | Meaning |
|------|---------|
| **starter** | Teach patterns / footguns — read these first |
| **smoke** | Short assert script for a public module |
| **cython-recipe** | Docs/sketch for cimport-only or ownership |
| **n/a** | No example surface |

**Start here:** [`STARTER.md`](STARTER.md) · [`pyhot.py`](pyhot.py) · [`py_cstr_bytes.py`](py_cstr_bytes.py) · overlap playbooks · core container scripts below.

**Barrel cimport (out-of-tree):** [`cimport_ext/`](cimport_ext/) — `from picop cimport …` against an installed package (`bash scripts/smoke_barrel_cimport.sh`).

(`cypy` still works as a deprecated alias until 3.0.)

```bash
pip install picop
# or: pip install "git+https://github.com/ckirua/picop.git"
for f in examples/py*.py examples/wrap_ansi.py; do python "$f" || exit 1; done
```

| Order | Module | Tier | Link / note |
|------:|--------|------|-------------|
| — | `picop.hot` | starter | [`pyhot.py`](pyhot.py) |
| — | C-string DX | starter | [`py_cstr_bytes.py`](py_cstr_bytes.py) |
| — | overlap: mapping vs dict | starter | [`py_overlap_mapping_vs_dict.py`](py_overlap_mapping_vs_dict.py) |
| — | overlap: sequence vs list | starter | [`py_overlap_sequence_vs_list.py`](py_overlap_sequence_vs_list.py) |
| — | overlap: str vs unicode | starter | [`py_overlap_str_vs_unicode.py`](py_overlap_str_vs_unicode.py) |
| 1 | `cytuple` | starter | [`pytuple.py`](pytuple.py) |
| 2 | `cybytes` | starter | [`pybytes.py`](pybytes.py) |
| 3 | `cydict` | starter | [`pydict.py`](pydict.py) |
| 4 | `cylist` | starter | [`pylist.py`](pylist.py) |
| 5 | `cyset` | starter | [`pyset.py`](pyset.py) |
| 6 | `cystr` | starter | [`pystr.py`](pystr.py) |
| 7 | `cyunicode` | smoke | [`pyunicode.py`](pyunicode.py) |
| 8 | `cyansi` | starter | [`wrap_ansi.py`](wrap_ansi.py) |
| 9 | `cygc` | smoke | [`pygc.py`](pygc.py) |
| 10 | `cyerr` | cython-recipe | see [cython/](cython/) + tracker |
| 11 | `cymem` | cython-recipe | see [cython/](cython/) + tracker |
| 12 | `cythread` | cython-recipe | see [cython/](cython/) + tracker |
| 13 | `cyatomic` | cython-recipe | see [cython/](cython/) + tracker |
| 14 | `cybytearray` | smoke | [`pybytearray.py`](pybytearray.py) |
| 15 | `cyarray` | smoke | [`pyarray.py`](pyarray.py) |
| 16 | `cymemoryview` | smoke | [`pymemoryview.py`](pymemoryview.py) |
| 17 | `cybuffer` | smoke | [`pybuffer.py`](pybuffer.py) |
| 18 | `cysequence` | smoke | [`pysequence.py`](pysequence.py) |
| 19 | `cyslice` | smoke | [`pyslice.py`](pyslice.py) |
| 20 | `cybool` | smoke | [`pybool.py`](pybool.py) |
| 21 | `cylong` | smoke | [`pylong.py`](pylong.py) |
| 22 | `cylongintrepr` | cython-recipe | see [cython/](cython/) + tracker |
| 23 | `cyfloat` | smoke | [`pyfloat.py`](pyfloat.py) |
| 24 | `cycomplex` | smoke | [`pycomplex.py`](pycomplex.py) |
| 25 | `cynumber` | smoke | [`pynumber.py`](pynumber.py) |
| 26 | `cyobject` | smoke | [`pyobject.py`](pyobject.py) |
| 27 | `cytype` | smoke | [`pytype.py`](pytype.py) |
| 28 | `cyref` | cython-recipe | see [cython/](cython/) + tracker |
| 29 | `cyfunction` | smoke | [`pyfunction.py`](pyfunction.py) |
| 30 | `cymethod` | smoke | [`pymethod.py`](pymethod.py) |
| 31 | `cymodule` | smoke | [`pymodule.py`](pymodule.py) |
| 32 | `cyiterator` | smoke | [`pyiterator.py`](pyiterator.py) |
| 33 | `cyiterobject` | smoke | [`pyiterobject.py`](pyiterobject.py) |
| 34 | `cygenobject` | smoke | [`pygenobject.py`](pygenobject.py) |
| 35 | `cycellobject` | smoke | [`pycellobject.py`](pycellobject.py) |
| 36 | `cydescr` | smoke | [`pydescr.py`](pydescr.py) |
| 37 | `cyinstance` | n/a | surface none (classic classes removed) |
| 38 | `cygetargs` | cython-recipe | see [cython/](cython/) + tracker |
| 39 | `cycodecs` | smoke | [`pycodecs.py`](pycodecs.py) |
| 40 | `cydatetime` | smoke | [`pydatetime.py`](pydatetime.py) |
| 41 | `cycontextvars` | smoke | [`pycontextvars.py`](pycontextvars.py) |
| 42 | `cymapping` | smoke | [`pymapping.py`](pymapping.py) |
| 43 | `cymarshal` | smoke | [`pymarshal.py`](pymarshal.py) |
| 44 | `cyfileobject` | smoke | [`pyfileobject.py`](pyfileobject.py) |
| 45 | `cypycapsule` | smoke | [`pypycapsule.py`](pypycapsule.py) |
| 46 | `cyweakref` | smoke | [`pyweakref.py`](pyweakref.py) |
| 47 | `cyceval` | cython-recipe | see [cython/](cython/) + tracker |
| 48 | `cypystate` | cython-recipe | see [cython/](cython/) + tracker |
| 49 | `cypylifecycle` | cython-recipe | see [cython/](cython/) + tracker |
| 50 | `cypyport` | cython-recipe | see [cython/](cython/) + tracker |
| 51 | `cyconversion` | smoke | [`pyconversion.py`](pyconversion.py) |
| 52 | `cyversion` | cython-recipe | see [cython/](cython/) + tracker |
| 53 | `cytime` | smoke | [`pytime.py`](pytime.py) |

## Cython recipes

| Doc | Topic |
|------|--------|
| [`cython/README.md`](cython/README.md) | cimport-only Orders |
| [`cython/borrow_vs_owned.md`](cython/borrow_vs_owned.md) | `dget`/`lget` ownership (DX-05) |

| Order | Module | Why not Python example |
|------:|--------|------------------------|
| 10 | `cyerr` | cimport-only ABI / process footguns |
| 11 | `cymem` | cimport-only ABI / process footguns |
| 12 | `cythread` | cimport-only ABI / process footguns |
| 13 | `cyatomic` | cimport-only ABI / process footguns |
| 22 | `cylongintrepr` | cimport-only ABI / process footguns |
| 28 | `cyref` | cimport-only ABI / process footguns |
| 37 | `cyinstance` | surface none on 3.14 |
| 38 | `cygetargs` | cimport-only ABI / process footguns |
| 47 | `cyceval` | cimport-only ABI / process footguns |
| 48 | `cypystate` | cimport-only ABI / process footguns |
| 49 | `cypylifecycle` | cimport-only ABI / process footguns |
| 50 | `cypyport` | cimport-only ABI / process footguns |
| 52 | `cyversion` | cimport-only ABI / process footguns |
