# Safety and trusted-caller footguns

`picop` wraps CPython C-API helpers for **known-type hot paths**. The former `cypy` Python package and Cython cimport shims were removed in 3.0. Some APIs skip checks that Python builtins always do. Misuse can crash the process or worse — treat them as **trusted-caller** tools, not as hardening against hostile input.

## Unchecked accessors (OOB is UB)

Helpers like `list_get`, `str_char_at`, and siblings assume the index (or shape) is already valid. Out-of-bounds access is **undefined behavior**.

Prefer:

- `list_get_checked` / `list_get_ref` when the index may be OOB
- Bounds you own in Cython (`0 <= i < list_len(xs)`) before calling unchecked getters

See also the ownership matrix in [`.cursor/skills/use-cypy/SKILL.md`](../.cursor/skills/use-cypy/SKILL.md).

## Borrowed pointers

C-string / UTF-8 borrow helpers (`uutf8`, `bas_string`, `bytes_as_string`, …) return pointers that **must not outlive** the owning Python object. Do not store them past the lifetime of `s` / `b`, and do not free them.

Prefer owning APIs when you need a durable value (e.g. `uutf8_bytes`).

`tb_next_borrow` returns a borrowed `PyObject *` and may be `NULL`; keep the
traceback alive for the whole walk.

## New-reference getters must not be double-increfed

`PyObject_Vectorcall`, `PyFrame_GetCode`, `PyFrame_GetBack`, `PyFrame_GetGenerator`,
`PyFrame_GetVar`, `PyFrame_GetVarString`, `PyFrame_New` and the `cy*_shim.h` field
readers return a **new** reference. Declaring such a C function as `PyObject *` and
returning `<object>result` increfs a reference Cython already owns — one leaked
object per call. Either declare the extern as `object` (Cython takes the reference)
or convert and release:

```pyx
cdef PyObject *result = PyObject_Vectorcall(<PyObject *>callable, args, nargsf, kwnames)
cdef object out = <object>result
Py_DECREF(result)
return out
```

The opposite direction matters just as much: macro getters such as `PyCell_GET`
return a **borrowed** pointer, so they must stay `PyObject *` and be promoted with
an `<object>` cast. Declaring them as `object` increfs a reference nobody owns and
drives the target's refcount down by one per call. Both directions are pinned by
`test_object_getters_hand_back_exactly_one_reference` in
[`tests/test_systems.py`](../tests/test_systems.py).

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
  `hash_buffer_raw(ptr, length)` and `hash_pointer(ptr)` are the trusted-caller
  versions of `hash_buffer`: the pointer must stay readable for the whole call, and
  `hash_pointer` is an identity hash, not the object's own `__hash__`.
- Noexcept memoryview metadata helpers require a valid, unreleased view. Stable
  acquired exports prevent resize/release, not concurrent writes by arbitrary
  exporters; synchronize content mutations separately.
- `UnicodeWriter` owns its internal buffer: `finish()` consumes the handle and any
  later call raises `RuntimeError` (never UB), `discard()` releases the buffer, and
  an unclosed writer's buffer is freed only at GC — use the context manager.
- `BytesWriter` uses the public `PyBytesWriter` API on CPython 3.15+ and mirrors
  CPython's internal `_PyBytesWriter` struct in `cybytes_shim.h` on 3.8-3.14.
  Note `PyBytesWriter_Create(size)` on 3.15+ pre-writes `size` bytes and
  `PyBytesWriter_Resize` also sets the logical size; the wrapper creates the
  writer at the hinted capacity and rewinds it to zero with `Resize(writer, 0)`,
  which never shrinks the allocation — `max_size` becomes reserved capacity on
  every supported version. `Prepare` can reallocate the buffer on every
  write, so the wrapper tracks the write position in its own handle; any pointer
  into the buffer captured earlier is invalid. Lifecycle guards
  (`RuntimeError` after `finish()`/`discard()`) prevent use-after-free.
- `tuple_from_array` INCREFs every array element (the caller keeps its own
  references), so it is safe over borrowed-reference arrays; negative sizes raise
  `ValueError` before any allocation.
- `interpreter_guard()` (CPython 3.15+) prevents interpreter finalization while
  open; an unclosed guard is closed at dealloc, and a guard is never reused after
  `__exit__`. `threadstate_ensure`/`threadstate_release` must be paired on the
  same thread — over-release is `Py_FatalError`, not an exception. Tokens are
  opaque `void*` sentinels (sometimes an internal non-`PyThreadState` value):
  never dereference or compare them. On CPython < 3.15 `guards_supported()` is
  False, `interpreter_guard()` raises `RuntimeError`, and the ensure/release
  helpers fall back to `PyGILState_Ensure`/`PyGILState_Release`.
- `ref_set_immortal` pins an object's reference count: the object is **never freed**, so use it only for long-lived singletons. It returns 0 (no pin) when the object is not uniquely referenced or is a str — mirroring CPython 3.15 `PyUnstable_SetImmortal`. On 3.14 the emulation works only in GIL builds; 3.14 free-threaded builds refuse the pin.
- Fill uninitialized bytes/tuple/list slots exclusively before publication.
  Unchecked cell setters retain their caller-managed reference-transfer rules.
- Direct `PyCodeObject` field reads use the cycode shim: object fields are returned as new references via `Py_NewRef`, while scalar fields are returned by value.
- Frame accessors return new references. Under free-threading, `frame_back`,
  `frame_generator`, and `frame_var` are not lock-protected; keep the frame alive
  for the entire call. Cython `cdef` locals are invisible to `frame_var`.
- C API calls require an attached thread state even with the GIL disabled.
  Object-domain allocators are for Python objects, not general-purpose buffers.

UUID values use real stdlib base storage and are immutable after construction.
Direct malicious mutation through base descriptors or `object.__setattr__` is
outside the concurrency contract. Rebuild downstream Cython extensions; the old
private UUID layout is not a binary compatibility promise.


## Locks (`cylock`, cimport-only)

`mutex_lock`, `mutex_unlock` and `mutex_is_locked` take a **borrowed** `PyMutex *`.
The mutex is a one-byte value your extension declares (`cdef PyMutex mu`); picop
never owns it and never reads its contents.

- The mutex must outlive every call that received its address. A stack-local
  `PyMutex` is fine for one critical section; do not keep the pointer past the
  scope that declared it.
- `PyMutex` is **not reentrant**: locking a mutex the current thread already holds
  parks the thread. Use `cython.critical_section` for the common "protect one
  object" case and reach for `cylock` only for locks Cython cannot express (a
  mutex stored in a C struct, or one shared with a library).
- Unlocking a mutex you do not hold is silent corruption — no check, no exception,
  no error code.
- `mutex_init` zeroes the struct; zero is CPython's unlocked state.

## `cymonitoring` (cimport-only)

`PyMonitoringState *` is interpreter-populated storage that the caller owns on the
stack. Cython does not zero `cdef PyMonitoringState states[19]` — an unentered
array measured 12 of 19 `active` bytes non-zero.

Measured on CPython 3.15.0rc2 (`-O3`), with the array pre-filled to a sentinel:

- `event_types` is **positional**, not id-keyed: `state_array[i]` is populated for
  `event_types[i]`, for `i` in `range(length)`. Passing `[LINE, PY_RETURN]` with
  `length == 2` wrote slots 0 and 1, not slots 5 and 2. `monitoring_scope` always
  passes `0..17` in id order, which is why slot `i` can be read as event `i`.
- `length` is not bounded and out-of-range ids are not rejected: with 100 ids
  `EnterScope` still returned 0, and an id of 255 left its slot untouched rather
  than raising. Keep the table in id order and never index past
  `PICOP_MONITORING_STATE_SLOTS` (19).
- The `version` argument is a memo. When `*version` already equals the
  interpreter's monitoring version, `EnterScope` returns 0 **without populating the
  array** — measured with a fresh array, `version = 0`, and no tool ever enabled.
  `monitoring_active` then reads stack garbage: correctness is unaffected (nothing
  is instrumented), but the caller-side gate stops saving anything. If that matters,
  `memset(states, 0, sizeof(states))` before the first scope.
- Slot 18 (`PY_MONITORING_EVENT_BRANCH`, deprecated in 3.14) is never written; it
  keeps whatever was on the stack.
- `active` is a tool bitmask (`1 << tool_id`), not a bool.
- Monitoring callbacks are Python objects and can raise; `fire_*` then returns `-1`
  and propagates the exception.

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
