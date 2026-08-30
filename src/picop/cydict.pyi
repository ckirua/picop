"""Typed C-API helpers for :class:`dict` hot paths.

Prefer :mod:`picop.cydict` (or starters in :mod:`picop.hot`) over builtin
``dict`` methods when the concrete type is known. See
:doc:`/user_guide/safety` for borrowed-ref and trusted-caller caveats, and
:doc:`/user_guide/quickstart` for import patterns.
"""

# Preferred public names (0.3 hard trim)

def dict_check(p: object) -> bool:
    """Return True if ``p`` is a :class:`dict` or subtype (``PyDict_Check``)."""
    ...

def dict_check_exact(p: object) -> bool:
    """Return True if ``type(p) is dict`` (``PyDict_CheckExact``)."""
    ...

def dict_clear(d: dict) -> None:
    """Clear ``d`` via ``PyDict_Clear``."""
    ...

def dict_contains(d: dict, key: str) -> bool:
    """Return whether ``key`` is in ``d`` (``PyDict_Contains``)."""
    ...

def dict_copy(d: dict) -> dict:
    """Return a shallow copy of ``d`` via ``PyDict_Copy``."""
    ...

def dict_del(d: dict, key: str) -> int:
    """Delete ``d[key]`` via ``PyDict_DelItem``.

    Notes
    -----
    Returns ``0`` on success and ``-1`` on error; errors raise. Do not use the
    status int as a bool.
    """
    ...

def dict_get(d: dict, key: str) -> object:
    """Return ``d[key]`` via borrowed ``PyDict_GetItem``.

    Notes
    -----
    Missing keys and stored ``None`` both yield ``None``. Prefer
    ``dict_get_ref`` when you need to distinguish those cases.
    """
    ...

def dict_get_ref(d: dict, key: object) -> object:
    """Return a strong ref to ``d[key]`` via ``PyDict_GetItemRef``.

    Notes
    -----
    Missing keys yield ``None``; a stored ``None`` is a distinct strong ref to
    ``None``. Prefer this over ``dict_get`` when that distinction matters.
    """
    ...

def dict_get_with_error(d: dict, key: object) -> object:
    """Return ``d[key]`` via ``PyDict_GetItemWithError``.

    Notes
    -----
    Hash/equality errors propagate. Missing keys yield ``None`` (same
    missing-vs-stored-``None`` ambiguity as ``dict_get``).
    """
    ...

def dict_len(d: dict) -> int:
    """Return ``len(d)`` via ``PyDict_GET_SIZE``."""
    ...

def dict_eq(a: dict, b: dict) -> bool:
    """Return True if typed dicts are equal (identity/size short-circuit + richcompare)."""
    ...

def dict_merge(d: dict, other: object, override: bool = True) -> int:
    """Merge ``other`` into ``d`` via ``PyDict_Merge``.

    Notes
    -----
    ``override`` controls whether existing keys are overwritten. Returns ``0``
    on success and ``-1`` on error; errors raise. Do not use the status int as
    a bool.
    """
    ...

def dict_merge_from_seq2(d: dict, seq2: object, override: bool = True) -> int:
    """Merge key/value pairs from ``seq2`` via ``PyDict_MergeFromSeq2``.

    Notes
    -----
    Returns ``0`` on success and ``-1`` on error; errors raise. Do not use the
    status int as a bool.
    """
    ...

def dict_new() -> dict:
    """Return a new empty :class:`dict` (``PyDict_New``)."""
    ...

def dict_pop(d: dict, key: str) -> object:
    """Remove ``key`` and return its value via ``PyDict_Pop``.

    Notes
    -----
    Missing keys yield ``None`` (same ambiguity as a stored ``None`` value).
    """
    ...

def dict_proxy(d: dict) -> object:
    """Return a read-only ``mappingproxy`` over ``d`` (``PyDictProxy_New``)."""
    ...

def dict_set(d: dict, key: str, value: object) -> int:
    """Set ``d[key] = value`` via ``PyDict_SetItem``.

    Notes
    -----
    Returns ``0`` on success and ``-1`` on error; errors raise. Do not use the
    status int as a bool.
    """
    ...

def dict_setdefault(d: dict, key: str, default: object = None) -> object:
    """Return ``d.setdefault(key, default)`` via borrowed ``PyDict_SetDefault``.

    Notes
    -----
    The returned reference is borrowed. Prefer ``dict_setdefault_ref`` when you
    need a strong ref.
    """
    ...

def dict_setdefault_ref(d: dict, key: object, default: object = None) -> object:
    """Return ``setdefault`` via strong-ref ``PyDict_SetDefaultRef``."""
    ...

def dict_size(d: object) -> int:
    """Return ``len(d)`` via checked ``PyDict_Size``.

    Notes
    -----
    Prefer ``dict_len`` on a typed ``dict`` hot path.
    """
    ...

def dict_update(d: dict, other: dict) -> int:
    """Update ``d`` from ``other`` via ``PyDict_Update``.

    Notes
    -----
    Returns ``0`` on success and ``-1`` on error; errors raise. Do not use the
    status int as a bool.
    """
    ...
