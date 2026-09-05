"""Generic ``PyObject`` helpers for attributes, calls, and richcompare.

Prefer builtins or typed Core helpers from Python when the type is known; use
equality and attribute helpers here for abstract objects. Tier A losers remain
``cpdef`` but are omitted from stubs. See :doc:`/user_guide/safety` for
``*_cstr`` name typing.
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
    """Return ``repr(o)`` via ``PyObject_Repr``."""
    ...

def obj_bytes(o: object) -> object:
    """Return ``bytes(o)`` via ``PyObject_Bytes``."""
    ...

def obj_issubclass(derived: object, cls: object) -> bool:
    """Return ``issubclass(derived, cls)`` via ``PyObject_IsSubclass``."""
    ...

def obj_call(callable_object: object, args: object, kw: object = None) -> object:
    """Call ``callable_object(*args, **kw)`` via ``PyObject_Call``.

    Notes
    -----
    ``args`` must be a tuple.
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
    On error raises — do not treat the result as a boolean success flag.
    """
    ...

def obj_dir(o: object) -> object:
    """Return ``dir(o)`` via ``PyObject_Dir``."""
    ...

def obj_iter(o: object) -> object:
    """Return ``iter(o)`` via ``PyObject_GetIter``."""
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
