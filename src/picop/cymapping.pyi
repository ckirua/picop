"""Abstract mapping-protocol helpers via the CPython C-API.

Use when the concrete type is unknown. Prefer typed ``dict_*`` from Core /
:mod:`picop.hot` when you know the object is a ``dict``. Tier A losers
(ratio > 1.02 vs Python) stay as ``cpdef`` but are omitted here. See
:doc:`/user_guide/safety` for ``*_cstr`` key typing.
"""

def map_check(o: object) -> bool:
    """Return True if ``o`` provides the mapping protocol."""
    ...

def map_eq(a: object, b: object) -> bool:
    """Return True if mappings are equal via identity/size short-circuit + richcompare.

    Notes
    -----
    Prefer ``dict_eq`` when both operands are known ``dict`` instances.
    """
    ...

def map_has_key(o: object, key: object) -> bool:
    """Return True if mapping ``o`` has ``key``."""
    ...

def map_del(o: object, key: object) -> int:
    """Delete ``o[key]`` via ``PyMapping_DelItem``.

    Notes
    -----
    Returns ``0`` on success; errors raise — do not use the status as a bool.
    """
    ...

def map_keys(o: object) -> object:
    """Return ``o.keys()`` via ``PyMapping_Keys``."""
    ...

def map_values(o: object) -> object:
    """Return ``o.values()`` via ``PyMapping_Values``."""
    ...

def map_items(o: object) -> object:
    """Return ``o.items()`` via ``PyMapping_Items``."""
    ...

def map_has_key_cstr(o: object, key: bytes) -> bool:
    """Return True if mapping ``o`` has C-string ``key``.

    Notes
    -----
    ``key`` must be ``bytes`` (ASCII/UTF-8), not ``str``. See
    :doc:`/user_guide/safety`. Alias of ``map_has_key_string`` (prefer ``*_cstr``).
    """
    ...

def map_del_cstr(o: object, key: bytes) -> int:
    """Delete ``o[key]`` via ``PyMapping_DelItemString``.

    Notes
    -----
    ``key`` must be ``bytes``, not ``str``. Returns ``0`` on success; errors
    raise — do not use the status as a bool. Alias of ``map_del_string``.
    """
    ...

def map_getitem_cstr(o: object, key: bytes) -> object:
    """Return ``o[key]`` via ``PyMapping_GetItemString``.

    Notes
    -----
    ``key`` must be ``bytes`` (ASCII/UTF-8), not ``str``. See
    :doc:`/user_guide/safety`. Alias of ``map_getitem_string`` (prefer ``*_cstr``).
    """
    ...

def map_setitem_cstr(o: object, key: bytes, v: object) -> int:
    """Set ``o[key] = v`` via ``PyMapping_SetItemString``.

    Notes
    -----
    ``key`` must be ``bytes``, not ``str``. Returns ``0`` on success; errors
    raise — do not use the status as a bool. Alias of ``map_setitem_string``.
    """
    ...
