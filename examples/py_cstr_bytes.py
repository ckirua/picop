"""Teach C-string APIs want ``bytes``, not ``str`` (DX-03).

Run: python examples/py_cstr_bytes.py
"""

from picop import codec_known, map_getitem_cstr

def main() -> None:
    d = {"a": 1}

    # Wrong: Python str where const char* / bytes is required
    try:
        map_getitem_cstr(d, "a")  # type: ignore[arg-type]
    except TypeError as exc:
        print(f"expected TypeError for str key: {exc}")
    else:
        raise AssertionError("str key should fail")

    # Right: bytes — prefer *_cstr names (N2)
    assert map_getitem_cstr(d, b"a") == 1
    assert codec_known(b"utf-8") is True
    try:
        codec_known("utf-8")  # type: ignore[arg-type]
    except TypeError as exc:
        print(f"expected TypeError for str encoding: {exc}")
    else:
        raise AssertionError("str encoding should fail")

    print("ok — use bytes for *_cstr / codec / C-string helpers")

if __name__ == "__main__":
    main()
