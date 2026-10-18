"""GIL-held CPython call helpers for Cython extensions."""


def call_noargs(callable: object) -> object:
    """Call ``callable`` without constructing an argument tuple."""
    ...


def call_onearg(callable: object, arg: object) -> object:
    """Call ``callable(arg)`` without constructing an argument tuple."""
    ...


def call_twoargs(callable: object, arg0: object, arg1: object) -> object:
    """Call ``callable(arg0, arg1)`` through CPython vectorcall."""
    ...
