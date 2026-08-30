"""Category facade: bytes / bytearray / array / memoryview / buffer / slice.

Typed buffer-adjacent Core helpers. Prefer ``bytes_len`` / ``bytes_contains`` /
``bytes_eq`` from ``picop.hot`` for the common bytes hot path.
See :doc:`/user_guide/safety` for borrowed C-string footguns.
"""

from __future__ import annotations

from .cyarray import array_check, array_check_exact, array_clone, array_eq, array_len, array_ne, array_zero
from .cybuffer import buf_check, buf_eq
from .cybytearray import (
    bytearray_check,
    bytearray_check_exact,
    bytearray_eq,
    bytearray_contains,
    bytearray_len,
    bytearray_ne,
    bytearray_size,
)
from .cybytes import (
    bytes_check,
    bytes_check_exact,
    bytes_contains,
    bytes_bytearray_eq,
    bytes_eq,
    bytes_ne,
    bytes_startswith,
    bytes_endswith,
    bytes_len,
    bytes_size,
)
from .cymemoryview import memoryview_check, memoryview_eq, memoryview_from_object, memoryview_ne
from .cyslice import slice_check, slice_eq, slice_new

__all__: tuple[str, ...] = (
    "bytes_check",
    "bytes_check_exact",
    "bytes_len",
    "bytes_size",
    "bytes_contains",
    "bytes_bytearray_eq",
    "bytes_eq",
    "bytes_ne",
    "bytes_startswith",
    "bytes_endswith",
    "bytearray_check",
    "bytearray_check_exact",
    "bytearray_eq",
    "bytearray_ne",
    "bytearray_contains",
    "bytearray_len",
    "bytearray_size",
    "array_check",
    "array_check_exact",
    "array_eq",
    "array_ne",
    "array_len",
    "array_clone",
    "array_zero",
    "memoryview_check",
    "memoryview_eq",
    "memoryview_ne",
    "memoryview_from_object",
    "buf_check",
    "buf_eq",
    "slice_check",
    "slice_eq",
    "slice_new",
)
