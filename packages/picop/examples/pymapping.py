"""Python usage for picop cymapping.

Run: python examples/pymapping.py
"""
from picop import map_check, map_eq, map_has_key, map_getitem_cstr

def main() -> None:
    d = {"a": 1}
    assert map_check(d)
    assert map_has_key(d, "a")
    assert map_getitem_cstr(d, b"a") == 1
    assert map_eq({"a": 1}, {"a": 1}) and not map_eq({"a": 1}, {"a": 2}) and map_eq({}, {})
    assert map_eq({"a": 1, "b": 2}, {"b": 2, "a": 1})  # order-independent
    print("ok", map_check(d))

if __name__ == "__main__":
    main()
