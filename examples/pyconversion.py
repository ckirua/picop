"""Python usage for picop cyconversion.

Run: python examples/pyconversion.py
"""
from picop import conv_cstr_to_double, conv_stricmp

def main() -> None:
    assert conv_cstr_to_double(b"3.5") == 3.5
    assert conv_stricmp(b"Ab", b"aB") == 0
    print("ok", conv_cstr_to_double(b"2"))

if __name__ == "__main__":
    main()
