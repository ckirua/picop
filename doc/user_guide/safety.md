# Safety

`picop` wraps CPython C-API helpers for **known-type hot paths**. Some APIs skip checks that Python builtins always do. Misuse can crash the process or worse — treat them as **trusted-caller** tools, not as hardening against hostile input.

## Unchecked accessors (OOB is UB)

Helpers like `list_get`, `str_char_at`, and siblings assume the index (or shape) is already valid. Out-of-bounds access is **undefined behavior**.

Prefer:

- `list_get_checked` / `list_get_ref` when the index may be OOB
- Bounds you own in Cython (`0 <= i < list_len(xs)`) before calling unchecked getters

## Borrowed pointers

C-string / UTF-8 borrow helpers (`uutf8`, `bas_string`, `bytes_as_string`, …) return pointers that **must not outlive** the owning Python object. Do not store them past the lifetime of `s` / `b`, and do not free them.

Prefer owning APIs when you need a durable value (e.g. `uutf8_bytes`).

## `marshal_loads`

Untrusted data is **unsafe** — same class as stdlib `marshal.loads`. Only deserialize marshal payloads from a trusted source.

## `*_cstr` wants `bytes`, not `str`

C-string helpers (`map_getitem_cstr`, …) take **`bytes`** (ASCII/UTF-8), not Python `str`. Passing `str` is a type error / footgun.

Runnable demo in the repository: `examples/py_cstr_bytes.py`.

## Reporting vulnerabilities

See the repository [`SECURITY.md`](https://github.com/ckirua/picop/blob/main/SECURITY.md).
