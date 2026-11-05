"""Python usage for picop cycode.

Run: python examples/pycode.py
"""
from picop import code_addr2line, code_check, code_firstlineno, code_name


def inner(value):
    return value + 1


def main() -> None:
    code = inner.__code__
    print("code_check:", code_check(code))
    print("code_name:", code_name(code))
    print("code_firstlineno:", code_firstlineno(code))
    print("code_addr2line:", code_addr2line(code, 0))


if __name__ == "__main__":
    main()
