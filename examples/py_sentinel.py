"""Python usage for picop cysentinel.

Run: python examples/py_sentinel.py
"""
import builtins
import sys

import picop
from picop import (
    sentinel_check,
    sentinel_check_exact,
    sentinel_new,
    sentinel_type,
)


def main() -> None:
    print(f"picop {picop.__version__} on CPython {sys.version_info.major}.{sys.version_info.minor}")

    # ``sentinel`` is a CPython 3.15 builtin. On 3.14 the helpers are still
    # importable: checks report False and the constructors raise.
    if not hasattr(builtins, "sentinel"):
        assert not sentinel_check(object())
        assert not sentinel_check_exact(object())
        try:
            sentinel_new("nope")
        except NotImplementedError:
            pass
        print("n/a — sentinel needs CPython 3.15+")
        return

    # ``sentinel_new`` takes a name and optional explicit module and repr.
    # Unlike the builtin constructor, the module is not inferred by default.
    missing = sentinel_new("missing")
    eof = sentinel_new("eof", module="examples.py_sentinel", repr="<eof>")

    assert missing.__name__ == "missing" and missing.__module__ is None
    assert eof.__name__ == "eof" and eof.__module__ == "examples.py_sentinel"
    assert repr(missing) == "missing" and repr(eof) == "<eof>"

    # Every sentinel is unique: sentinels only compare equal to themselves.
    assert missing is not eof
    assert missing != eof
    assert missing == missing
    assert bool(missing)  # sentinels are always truthy

    assert sentinel_check(missing) and sentinel_check_exact(missing)
    assert sentinel_check(eof) and sentinel_check_exact(eof)
    assert not sentinel_check(None)
    assert not sentinel_check_exact(0)
    assert not sentinel_check(missing.__class__)

    # ``sentinel_type()`` hands back the builtin ``sentinel`` *type*, which
    # is the class the instances above are made of, not a sentinel instance.
    builtin_type = sentinel_type()
    assert builtin_type is builtins.sentinel
    assert missing.__class__ is builtin_type
    assert not sentinel_check(builtin_type)
    assert not sentinel_check_exact(builtin_type)

    try:
        sentinel_new(1)
    except TypeError:
        pass  # the name must be a str
    else:
        raise AssertionError("sentinel_new(1) should raise TypeError")

    print("ok", builtin_type, missing, eof)


if __name__ == "__main__":
    main()
