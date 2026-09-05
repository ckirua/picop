"""Smoke checks for the provisional :mod:`picop.protocols` facade."""

from __future__ import annotations

import picop.protocols as protocols
from picop.protocols import (
    map_check,
    map_eq,
    map_has_key,
    num_check,
    num_eq,
    obj_eq,
    seq_check,
    seq_contains,
    seq_eq,
    seq_get,
)


def test_protocols_all_matches_stubbed_surface() -> None:
    assert protocols.__all__ == (
        "map_check",
        "map_eq",
        "map_has_key",
        "seq_check",
        "seq_eq",
        "seq_get",
        "seq_contains",
        "num_check",
        "num_eq",
        "obj_eq",
    )
    for name in protocols.__all__:
        assert getattr(protocols, name) is not None


def test_obj_eq() -> None:
    xs = [1, 2, 3]
    assert obj_eq(xs, [1, 2, 3]) is True
    assert obj_eq(xs, [1, 2]) is False
    assert obj_eq(xs, xs) is True
    assert obj_eq("a", "a") is True
    assert obj_eq("a", "b") is False


def test_num_check_and_num_eq() -> None:
    assert num_check(3) is True
    assert num_check(1.5) is True
    assert num_check("x") is False
    assert num_eq(1, 1) is True
    assert num_eq(1, 2) is False
    assert num_eq(1.5, 1.5) is True
    assert num_eq(0.0, -0.0) is True
    assert num_eq(1, 1.0) is True
    nan = float("nan")
    assert num_eq(nan, nan) is False


def test_seq_check_get_eq_contains() -> None:
    assert seq_check([1, 2]) is True
    assert seq_check((1, 2)) is True
    assert seq_check("ab") is True
    assert seq_check(3) is False
    assert seq_get([1, 2, 3], 1) == 2
    assert seq_get("ab", 0) == "a"
    assert seq_eq([1, 2], [1, 2]) is True
    assert seq_eq([1], [2]) is False
    assert seq_eq((1, 2), (1, 2)) is True
    assert seq_eq((1, 2), [1, 2]) is False
    assert seq_contains([1, 2, 3], 2) is True
    assert seq_contains([1, 2, 3], 9) is False
    assert seq_contains("abc", "b") is True


def test_map_check_eq_has_key() -> None:
    d = {"a": 1}
    assert map_check(d) is True
    # PyMapping_Check is true for list/str/tuple too; use a non-subscriptable.
    assert map_check(3) is False
    assert map_has_key(d, "a") is True
    assert map_has_key(d, "missing") is False
    assert map_eq({"a": 1}, {"a": 1}) is True
    assert map_eq({"a": 1}, {"a": 2}) is False
    assert map_eq({"a": 1, "b": 2}, {"b": 2, "a": 1}) is True
