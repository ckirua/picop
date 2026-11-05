"""Python usage for picop cyfrozendict.

Run: python examples/pyfrozendict.py
"""
from picop import (
    anydict_check,
    anydict_check_exact,
    anydict_len,
    frozendict_check,
    frozendict_check_exact,
    frozendict_empty,
    frozendict_new,
)


def main() -> None:
    try:
        frozen = frozendict_new({"a": 1, "b": 2})
    except NotImplementedError:
        print("skipped — frozendict needs CPython 3.15+")
        return

    # frozendict is NOT a dict subclass: dict-shaped checks say False.
    assert not isinstance(frozen, dict)
    assert frozendict_check(frozen) and frozendict_check_exact(frozen)
    assert not frozendict_check({})
    assert anydict_check(frozen) and anydict_check({})
    assert anydict_check_exact(frozen) and anydict_check_exact({})
    assert not anydict_check([1, 2])

    # Copying a frozendict must go through the constructor: PyDict_Copy rejects it.
    assert frozendict_new(frozen) == frozen
    assert frozendict_empty() == frozendict()
    assert anydict_len(frozen) == len(frozen) == 2
    print("ok", frozen, anydict_len(frozen))


if __name__ == "__main__":
    main()
