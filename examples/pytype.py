"""Python usage for picop cytype.

Run: python examples/pytype.py
"""
from picop.cytype import type_check, type_check_exact, type_eq, type_is_subtype
from picop.cytype import type_get_name, type_get_qualname, type_get_dict


def main() -> None:
    assert type_check(int) and type_check_exact(int)
    assert type_is_subtype(bool, int)
    assert type_eq(int, int) and not type_eq(int, str)
    assert type_eq(bool, bool) and not type_eq(bool, int)
    assert type_get_name(int) == "int"
    assert type_get_qualname(int) == "int"
    assert isinstance(type_get_dict(int), dict)
    assert type_get_dict(int) is not int.__dict__

    def outer():
        class Nested:
            pass
        return Nested

    assert type_get_qualname(outer()) == "main.<locals>.outer.<locals>.Nested"
    print("ok", type_is_subtype(bool, int))


if __name__ == "__main__":
    main()
