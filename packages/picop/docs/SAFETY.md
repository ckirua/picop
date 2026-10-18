# Safety and trusted-caller footguns

`picop` wraps CPython C-API helpers for **known-type hot paths** (deprecated soft alias: `cypy`, removed in **3.0**). Some APIs skip checks that Python builtins always do. Misuse can crash the process or worse — treat them as **trusted-caller** tools, not as hardening against hostile input.

## Unchecked accessors (OOB is UB)

Helpers like `list_get`, `str_char_at`, and siblings assume the index (or shape) is already valid. Out-of-bounds access is **undefined behavior**.

Prefer:

- `list_get_checked` / `list_get_ref` when the index may be OOB
- Bounds you own in Cython (`0 <= i < list_len(xs)`) before calling unchecked getters

See also the ownership matrix in [`.cursor/skills/use-cypy/SKILL.md`](../.cursor/skills/use-cypy/SKILL.md).

## Borrowed pointers

C-string / UTF-8 borrow helpers (`uutf8`, `bas_string`, `bytes_as_string`, …) return pointers that **must not outlive** the owning Python object. Do not store them past the lifetime of `s` / `b`, and do not free them.

Prefer owning APIs when you need a durable value (e.g. `uutf8_bytes`).

## Free-threaded callers

The supported runtimes are 3.14, 3.15, 3.14t and 3.15t; t imports must not enable
the GIL. Helpers retain an owning result while holding the relevant object's
critical section where borrowed CPython access would otherwise race replacement.
That does not remove trusted-caller preconditions:

- Keep an unchecked index valid for the entire call. A prior length check alone
  is not sufficient if another thread can shrink the list.
- Hold the dictionary critical section across **the entire iteration and use of
  borrowed outputs** from `dict_next`/`dnext`, not just the call to `PyDict_Next`.
- Escaping array/list/buffer/memoryview pointers require an owning object and
  external lifetime/mutation synchronization. No lock remains held after return.
- Noexcept memoryview metadata helpers require a valid, unreleased view. Stable
  acquired exports prevent resize/release, not concurrent writes by arbitrary
  exporters; synchronize content mutations separately.
- Fill uninitialized bytes/tuple/list slots exclusively before publication.
  Unchecked cell setters retain their caller-managed reference-transfer rules.
- C API calls require an attached thread state even with the GIL disabled.
  Object-domain allocators are for Python objects, not general-purpose buffers.

UUID values use real stdlib base storage and are immutable after construction.
Direct malicious mutation through base descriptors or `object.__setattr__` is
outside the concurrency contract. Rebuild downstream Cython extensions; the old
private UUID layout is not a binary compatibility promise.


## `marshal_loads`

Untrusted data is **unsafe** — same class as stdlib `marshal.loads`. Only deserialize marshal payloads from a trusted source.

## `*_cstr` wants `bytes`, not `str`

C-string helpers (`map_getitem_cstr`, …) take **`bytes`** (ASCII/UTF-8), not Python `str`. Passing `str` is a type error / footgun.

Runnable demo: [`examples/py_cstr_bytes.py`](../examples/py_cstr_bytes.py).

## Monkey experiments (not shipped)

Builtin monkey-patch experiments are **archived** and are **not** part of the package:

[`docs/future/MONKEY.md`](future/MONKEY.md)

## Reporting real vulns

See [`SECURITY.md`](../SECURITY.md).
