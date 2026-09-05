from __future__ import annotations

import pytest

from picop import (
    buf_itemsize,
    buf_nbytes,
    buf_ndim,
    buf_readonly,
    call_noargs,
    call_onearg,
    call_twoargs,
    memoryview_itemsize,
    memoryview_nbytes,
    memoryview_ndim,
    memoryview_readonly,
)


def test_call_helpers_preserve_results_and_exceptions() -> None:
    assert call_noargs(lambda: "ok") == "ok"
    assert call_onearg(lambda value: value * 2, 3) == 6
    assert call_twoargs(lambda left, right: left + right, 2, 5) == 7
    with pytest.raises(ValueError):
        call_noargs(lambda: (_ for _ in ()).throw(ValueError("bad")))


def test_buffer_inspection_matches_memoryview_metadata() -> None:
    writable = bytearray(b"abc")
    readonly = b"abc"
    assert (buf_nbytes(writable), buf_itemsize(writable), buf_ndim(writable)) == (3, 1, 1)
    assert buf_readonly(writable) is False
    assert buf_readonly(readonly) is True
    view = memoryview(readonly)
    assert (memoryview_nbytes(view), memoryview_itemsize(view), memoryview_ndim(view)) == (3, 1, 1)
    assert memoryview_readonly(view) is True
