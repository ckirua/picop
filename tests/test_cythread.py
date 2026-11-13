"""Order 077: interpreter guard context manager (cythread)."""

from __future__ import annotations

import sys

import pytest

from picop import guards_supported, interpreter_guard


def test_guards_supported_matches_version() -> None:
    assert guards_supported() is (sys.version_info >= (3, 15))


@pytest.mark.skipif(sys.version_info < (3, 15), reason="interpreter guards require 3.15+")
def test_guard_context_round_trip() -> None:
    with interpreter_guard() as guard:
        assert guard is not None
    guard = interpreter_guard()
    del guard  # unclosed guard is closed on dealloc, never leaks


@pytest.mark.skipif(sys.version_info < (3, 15), reason="interpreter guards require 3.15+")
def test_guard_double_exit_is_safe() -> None:
    guard = interpreter_guard()
    with guard:
        pass
    with guard:
        pass


@pytest.mark.skipif(sys.version_info >= (3, 15), reason="pre-3.15 fallback behaviour")
def test_guard_raises_before_315() -> None:
    with pytest.raises(RuntimeError):
        interpreter_guard()
