"""Generic ``PyObject`` helpers for attributes, calls, and richcompare.

Prefer builtins or typed Core helpers from Python when the type is known; use
equality and attribute helpers here for abstract objects. Tier A losers remain
``cpdef`` and carry a parity note in the stub. See :doc:`/user_guide/safety`
for ``*_cstr`` name typing.
"""

def obj_richcompare(o1: object, o2: object, opid: int) -> object:
    """Return rich comparison of ``o1`` and ``o2`` for ``opid`` (``Py_EQ`` …)."""
    ...

def obj_richcompare_bool(o1: object, o2: object, opid: int) -> bool:
    """Return rich comparison as bool for ``opid`` (``PyObject_RichCompareBool``)."""
    ...

def obj_eq(a: object, b: object) -> bool:
    """Return True if ``a == b`` via ``PyObject_RichCompareBool``.

    Notes
    -----
    Identity short-circuit applies. Prefer typed ``*_eq`` when both operands
    have a known Core type.
    """
    ...

def obj_setattr(o: object, name: object, v: object) -> int:
    """Set attribute ``name`` on ``o`` via ``PyObject_SetAttr``.

    Notes
    -----
    Returns ``0`` on success; errors raise — do not use the status as a bool.
    """
    ...

def obj_delattr(o: object, name: object) -> int:
    """Delete attribute ``name`` on ``o`` via ``PyObject_DelAttr``.

    Notes
    -----
    Returns ``0`` on success; errors raise — do not use the status as a bool.
    """
    ...

def obj_repr(o: object) -> object:
    """Return ``repr(o)`` via ``PyObject_Repr``.

    Notes
    -----
    Slower than the plain-Python equivalent ``repr(x)`` (Tier A 1.04x); last-resort
    bridge for unknown objects.
    """
    ...

def obj_bytes(o: object) -> object:
    """Return ``bytes(o)`` via ``PyObject_Bytes``."""
    ...

def obj_issubclass(derived: object, cls: object) -> bool:
    """Return ``issubclass(derived, cls)`` via ``PyObject_IsSubclass``.

    Notes
    -----
    Slower than the plain-Python equivalent ``issubclass(a, b)`` (Tier A 1.07x);
    last-resort bridge for unknown objects.
    """
    ...

def obj_call(callable_object: object, args: object, kw: object = None) -> object:
    """Call ``callable_object(*args, **kw)`` via ``PyObject_Call``.

    Notes
    -----
    ``args`` must be a tuple; ``kw`` must be a dict or ``None`` (no keywords).
    """
    ...

def obj_call_object(callable_object: object, args: object) -> object:
    """Call ``callable_object(*args)`` via ``PyObject_CallObject``."""
    ...

def obj_not(o: object) -> bool:
    """Return ``not o`` via ``PyObject_Not``."""
    ...

def obj_length_hint(o: object, default_value: int) -> int:
    """Return ``operator.length_hint(o, default_value)`` via ``PyObject_LengthHint``."""
    ...

def obj_setitem(o: object, key: object, v: object) -> int:
    """Set ``o[key] = v`` via ``PyObject_SetItem``.

    Notes
    -----
    Returns ``0`` on success; errors raise — do not use the status as a bool.
    """
    ...

def obj_delitem(o: object, key: object) -> int:
    """Delete ``o[key]`` via ``PyObject_DelItem``.

    Notes
    -----
    Returns ``0`` on success; errors raise — do not use the status as a bool.
    """
    ...

def obj_as_fd(o: object) -> int:
    """Return a file descriptor via ``PyObject_AsFileDescriptor``.

    Notes
    -----
    Slower than the plain-Python equivalent ``x.fileno()`` (Tier A 1.09x); last-
    resort bridge for unknown objects.

    On error raises — do not treat the result as a boolean success flag.
    """
    ...

def obj_dir(o: object) -> object:
    """Return ``dir(o)`` via ``PyObject_Dir``."""
    ...

def obj_iter(o: object) -> object:
    """Return ``iter(o)`` via ``PyObject_GetIter``.

    Notes
    -----
    Slower than the plain-Python equivalent ``iter(x)`` (Tier A 1.03x); last-resort
    bridge for unknown objects.
    """
    ...

def obj_format(obj: object, format_spec: object) -> object:
    """Return ``format(obj, format_spec)`` via ``PyObject_Format``."""
    ...

def obj_setattr_cstr(o: object, name: bytes, v: object) -> int:
    """Set C-string attribute ``name`` on ``o`` via ``PyObject_SetAttrString``.

    Notes
    -----
    ``name`` must be ``bytes``, not ``str``. Returns ``0`` on success; errors
    raise — do not use the status as a bool. Alias of ``obj_setattr_string``.
    """
    ...

def obj_delattr_cstr(o: object, name: bytes) -> int:
    """Delete C-string attribute ``name`` via ``PyObject_DelAttrString``.

    Notes
    -----
    ``name`` must be ``bytes``, not ``str``. Returns ``0`` on success; errors
    raise — do not use the status as a bool. Alias of ``obj_delattr_string``.
    """
    ...

def obj_callable(o: object) -> bool:
    """Return True if ``o`` is callable (``PyCallable_Check``).

    Notes
    -----
    Mixed Tier A parity: 0.97x (int), 1.12x (len); last-resort bridge for unknown
    objects.
    """
    ...

def obj_getattr(o: object, name: object) -> object:
    """Return ``getattr(o, name)`` via ``PyObject_GetAttr``.

    Notes
    -----
    Slower than the plain-Python equivalent ``getattr(x, name)`` (Tier A 1.05x);
    last-resort bridge for unknown objects.
    """
    ...

def obj_getattr_cstr(o: object, name: bytes) -> object:
    """Return the attribute named by a C string (``PyObject_GetAttrString``)."""
    ...

def obj_getitem(o: object, key: object) -> object:
    """Return ``o[key]`` via ``PyObject_GetItem``."""
    ...

def obj_hasattr(o: object, name: object) -> bool:
    """Return True if ``o`` has attribute ``name`` (``PyObject_HasAttr``).

    Notes
    -----
    Slower than the plain-Python equivalent ``hasattr(x, name)`` (Tier A
    1.16–1.21x); last-resort bridge for unknown objects.
    """
    ...

def obj_hasattr_cstr(o: object, name: bytes) -> bool:
    """Return True if ``o`` has the attribute named by a C string (``PyObject_HasAttrString``)."""
    ...

def obj_hash(o: object) -> int:
    """Return the hash of ``o`` (``PyObject_Hash``).

    Notes
    -----
    Slower than the plain-Python equivalent ``hash(x)`` (Tier A 1.22x); last-resort
    bridge for unknown objects.
    """
    ...

def obj_isinstance(inst: object, cls: object) -> bool:
    """Return True if ``inst`` is an instance of ``cls`` (``PyObject_IsInstance``).

    Notes
    -----
    Slower than the plain-Python equivalent ``isinstance(x, t)`` (Tier A 1.26x);
    last-resort bridge for unknown objects.
    """
    ...

def obj_istrue(o: object) -> bool:
    """Return the truthiness of ``o`` (``PyObject_IsTrue``).

    Notes
    -----
    Mixed Tier A parity: 1.00x (dict), 1.30x (0); last-resort bridge for unknown
    objects.
    """
    ...

def obj_len(o: object) -> int:
    """Return ``len(o)`` via ``PyObject_Length``."""
    ...

def obj_size(o: object) -> int:
    """Return ``Py_SIZE``-style length via ``PyObject_Size`` (alias of ``obj_len``).

    Notes
    -----
    Slower than the plain-Python equivalent ``len(x)`` (Tier A 1.15x); last-resort
    bridge for unknown objects.
    """
    ...

def obj_str(o: object) -> object:
    """Return ``str(o)`` via ``PyObject_Str``.

    Notes
    -----
    Slower than the plain-Python equivalent ``str(x)`` (Tier A 1.13x); last-resort
    bridge for unknown objects.
    """
    ...

def obj_type(o: object) -> object:
    """Return the type of ``o`` (``Py_TYPE``)."""
    ...
