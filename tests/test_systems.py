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
    code_addr2line,
    code_argcount,
    code_cellvars,
    code_check,
    code_code,
    code_consts,
    code_filename,
    code_firstlineno,
    code_freevars,
    code_kwonlyargcount,
    code_name,
    code_names,
    code_posonlyargcount,
    code_qualname,
    code_varnames,
    tb_check,
    tb_depth,
    tb_frame,
    tb_lasti,
    tb_lineno,
    tb_next,
    frame_back,
    frame_builtins,
    frame_check,
    frame_code,
    frame_generator,
    frame_globals,
    frame_lasti,
    frame_lineno,
    frame_var,
    frame_var_cstr,
    memoryview_itemsize,
    memoryview_nbytes,
    memoryview_ndim,
    memoryview_readonly,
    obj_call,
    sentinel_check,
    sentinel_check_exact,
    sentinel_new,
    sentinel_type,
)

def test_code_readers() -> None:
    def outer(prefix):
        captured = prefix

        def inner(posonly, /, regular, *, keyword):
            local = captured + regular + keyword
            return local

        return inner

    function = outer("value")
    code = function.__code__
    assert code_check(code)
    assert code_name(code) == "inner"
    assert code_qualname(code).endswith("outer.<locals>.inner")
    assert code_filename(code) == __file__
    assert code_firstlineno(code) > 0
    assert code_argcount(code) == 2
    assert code_posonlyargcount(code) == 1
    assert code_kwonlyargcount(code) == 1
    assert isinstance(code_consts(code), tuple)
    assert isinstance(code_names(code), tuple)
    assert code_varnames(code) == ("posonly", "regular", "keyword", "local")
    assert code_cellvars(code) == ()
    assert code_freevars(code) == ("captured",)


def test_code_addr2line() -> None:
    def target(value):
        result = value + 1
        return result

    code = target.__code__
    assert code_addr2line(code, 0) == code.co_firstlineno
    assert code_addr2line(code, 4) == code.co_firstlineno + 1


def test_code_check_rejects_non_code() -> None:
    assert not code_check(lambda: None)
    assert not code_check(None)


def test_traceback_readers() -> None:
    import sys

    def leaf() -> None:
        raise ValueError("boom")

    def mid() -> None:
        leaf()

    def top() -> None:
        mid()

    try:
        top()
    except ValueError:
        tb = sys.exc_info()[2]

    assert tb_check(tb) is True
    assert tb_lineno(tb) == tb.tb_lineno
    assert tb_lasti(tb) == tb.tb_lasti
    assert tb_frame(tb) is tb.tb_frame
    assert tb_next(tb) is not None


def test_traceback_chain_depth() -> None:
    import sys

    def leaf() -> None:
        raise ValueError("boom")

    def mid() -> None:
        leaf()

    def top() -> None:
        mid()

    try:
        top()
    except ValueError:
        tb = sys.exc_info()[2]

    count = 0
    current = tb
    while current is not None:
        count += 1
        current = current.tb_next
    assert tb_depth(tb) == count == 4
    assert tb_next(tb_next(tb_next(tb))) is not None


def test_tb_check_rejects_non_traceback() -> None:
    assert tb_check(None) is False
    assert tb_check(1) is False



def test_frame_helpers() -> None:
    import sys

    def inner():
        value = 42
        return sys._getframe()

    frame = inner()
    assert frame_check(frame)
    assert not frame_check(1)
    assert not frame_check(None)
    assert frame_lineno(frame) == frame.f_lineno
    assert frame_lasti(frame) == frame.f_lasti
    assert frame_code(frame) is frame.f_code
    assert frame_globals(frame) is frame.f_globals
    assert frame_builtins(frame) is frame.f_builtins
    assert frame_var(frame, "value") == 42
    assert frame_var_cstr(frame, b"value") == 42


def test_frame_var_propagates_name_error() -> None:
    import sys

    with pytest.raises(NameError):
        frame_var(sys._getframe(), "missing")


def test_frame_generator_identity() -> None:
    generator = (value for value in range(3))
    next(generator)
    assert frame_generator(generator.gi_frame) is generator


def test_frame_chain_back() -> None:
    import sys

    def inner():
        return sys._getframe()

    def outer():
        return inner()

    inner_frame = outer()
    assert frame_back(frame_back(frame_back(inner_frame))) is not None


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
