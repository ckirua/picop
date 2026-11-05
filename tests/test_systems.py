from __future__ import annotations

import builtins

import pytest

from picop import (
    buf_itemsize,
    buf_nbytes,
    buf_ndim,
    buf_readonly,
    call_noargs,
    call_onearg,
    call_twoargs,
    obj_call,
    memoryview_itemsize,
    memoryview_nbytes,
    memoryview_ndim,
    memoryview_readonly,
    sentinel_check,
    sentinel_check_exact,
    sentinel_new,
    sentinel_type,
)


@pytest.mark.skipif(not hasattr(builtins, "sentinel"), reason="requires Python 3.15 sentinel")
def test_sentinel_checks() -> None:
    value = sentinel_new("runtime_helper_test")
    builtin_value = builtins.sentinel("runtime_helper_test")
    assert sentinel_check(value) is True
    assert sentinel_check_exact(value) is True
    assert sentinel_check(builtin_value) is True
    assert sentinel_check_exact(builtin_value) is True
    for ordinary in (None, 0, {}, dict, lambda: None):
        assert sentinel_check(ordinary) is False
        assert sentinel_check_exact(ordinary) is False


@pytest.mark.skipif(not hasattr(builtins, "sentinel"), reason="requires Python 3.15 sentinel")
def test_sentinel_new_defaults_and_name_type() -> None:
    value = sentinel_new("runtime_helper_defaults")
    assert sentinel_check(value) is True
    assert repr(value) == "runtime_helper_defaults"
    with pytest.raises(TypeError):
        sentinel_new(1)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        sentinel_new("x", module=1)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        sentinel_new("x", repr=1)  # type: ignore[arg-type]
    configured = sentinel_new("eof", module="tests", repr="<eof>")
    assert configured.__name__ == "eof"
    assert configured.__module__ == "tests"
    assert repr(configured) == "<eof>"


@pytest.mark.skipif(not hasattr(builtins, "sentinel"), reason="requires Python 3.15 sentinel")
def test_sentinel_new_unicode_and_embedded_nul_boundary() -> None:
    value = sentinel_new("caf\u00e9", module="tests\u03bb", repr="<\u03bb>")
    assert value.__name__ == "caf\u00e9"
    assert value.__module__ == "tests\u03bb"
    assert repr(value) == "<\u03bb>"
    for name, module, representation in (
        ("bad\0name", None, None),
        ("x", "bad\0module", None),
        ("x", None, "bad\0repr"),
    ):
        with pytest.raises(ValueError, match="embedded NUL"):
            sentinel_new(name, module=module, repr=representation)


def test_sentinel_type_unsupported_on_314() -> None:
    if hasattr(builtins, "sentinel"):
        pytest.skip("3.15+ provides sentinel")
    with pytest.raises(NotImplementedError):
        sentinel_type()
    with pytest.raises(NotImplementedError):
        sentinel_new("unsupported")


@pytest.mark.skipif(not hasattr(builtins, "sentinel"), reason="requires Python 3.15 sentinel")
def test_sentinel_type_is_stable_and_exact() -> None:
    value = sentinel_type()
    assert value is builtins.sentinel
    assert sentinel_type() is builtins.sentinel
    assert sentinel_check_exact(sentinel_type()) is False
    assert sentinel_check_exact(sentinel_new("runtime_helper_marker")) is True


def test_call_helpers_preserve_results_and_exceptions() -> None:
    assert call_noargs(lambda: "ok") == "ok"
    assert call_onearg(lambda value: value * 2, 3) == 6
    assert call_twoargs(lambda left, right: left + right, 2, 5) == 7
    with pytest.raises(ValueError):
        call_noargs(lambda: (_ for _ in ()).throw(ValueError("bad")))


def test_obj_call_optional_keywords_and_exception_identity() -> None:
    def target(value: int, *, offset: int = 0) -> int:
        return value + offset

    assert obj_call(target, (4,)) == 4
    assert obj_call(target, (4,), {"offset": 3}) == 7

    failure = LookupError("callback failed")

    def fail() -> None:
        raise failure

    with pytest.raises(LookupError) as caught:
        obj_call(fail, ())
    assert caught.value is failure


def test_buffer_inspection_matches_memoryview_metadata() -> None:
    writable = bytearray(b"abc")
    readonly = b"abc"
    assert (buf_nbytes(writable), buf_itemsize(writable), buf_ndim(writable)) == (3, 1, 1)
    assert buf_readonly(writable) is False
    assert buf_readonly(readonly) is True
    view = memoryview(readonly)
    assert (memoryview_nbytes(view), memoryview_itemsize(view), memoryview_ndim(view)) == (3, 1, 1)
    assert memoryview_readonly(view) is True
