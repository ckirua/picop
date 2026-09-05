# External barrel `cimport` smoke

Regression check that **`from picop cimport …`** (package barrel via `__init__.pxd`) and submodule paths both cythonize against an **installed** `picop` (editable or wheel).

(`cypy` still works as a deprecated alias until 3.0.)

## Prerequisites

```bash
# from repo root
pip install -e . --no-build-isolation
# or: pip install dist/picop-*.whl
```

## Build + assert

```bash
# from repo root
bash scripts/smoke_barrel_cimport.sh
```

Or manually:

```bash
cd examples/cimport_ext
python setup.py build_ext --inplace
python -c "import demo; assert demo.check_barrel(); assert demo.check_submodule() == 2"
```

`demo.pyx` uses barrel (`bytes_eq`, `list_len`, `str_eq`) and `from picop.cybytes cimport bytes_len`.
