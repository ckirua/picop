"""Curated micro-opt starters — prefer ``from picop.hot import …`` over the flat barrel.

**Core frozen at 1.0** — this ``__all__`` is part of the stable Core surface
(additive minors OK; removals need a major). Full public surface remains on
``picop`` / ``picop.cy*``. Soft letter/bare aliases were removed in 0.3.
See :doc:`/user_guide/quickstart` and :doc:`/user_guide/safety`.
"""

from __future__ import annotations

from .cyansi import ansi_fg8, ansi_strip, ansi_wrap
from .cybytes import bytes_contains, bytes_eq, bytes_len, bytes_endswith, bytes_ne, bytes_startswith
from .cybytearray import bytearray_contains, bytearray_eq, bytearray_ne
from .cyarray import array_eq, array_ne
from .cymemoryview import memoryview_eq, memoryview_ne
from .cydict import dict_contains, dict_get, dict_len, dict_pop, dict_set, dict_setdefault
from .cylist import list_append, list_get, list_get_checked, list_len
from .cyset import set_add, set_contains
from .cystr import str_contains, str_eq, str_len
from .cytuple import tuple_get, tuple_len, tuple_pack2

__all__: tuple[str, ...] = (
    # dict
    "dict_get",
    "dict_set",
    "dict_len",
    "dict_contains",
    "dict_pop",
    "dict_setdefault",
    # list
    "list_len",
    "list_get",
    "list_get_checked",
    "list_append",
    # set
    "set_contains",
    "set_add",
    # tuple
    "tuple_len",
    "tuple_get",
    "tuple_pack2",
    # bytes
    "bytes_len",
    "bytes_contains",
    "bytes_eq",
    "bytes_ne",
    "bytes_startswith",
    "bytes_endswith",
    # bytearray
    "bytearray_eq",
    "bytearray_ne",
    "bytearray_contains",
    # array
    "array_eq",
    "array_ne",
    # memoryview
    "memoryview_eq",
    "memoryview_ne",
    # str
    "str_len",
    "str_eq",
    "str_contains",
    # ansi
    "ansi_wrap",
    "ansi_fg8",
    "ansi_strip",
)
