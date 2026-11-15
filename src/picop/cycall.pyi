"""GIL-held CPython call helpers for Cython extensions.

Public (``picop.hot``): ``call_noargs``, ``call_onearg``, ``call_twoargs``.
Cython-only (``cimport cycall``): ``call_vector``, ``call_method_noargs``,
``call_method_onearg``, ``call_method_vector``, ``vectorcall_nargs`` — these
take raw borrowed argument vectors and cannot be called from Python.
"""


def call_noargs(callable: object) -> object:
    """Call ``callable`` without constructing an argument tuple.

    Notes
    -----
    Mixed Tier A parity: 0.96x (3.14: zero args), 1.08x (3.15: zero args); the typed
    Cython call site.
    """
    ...


def call_onearg(callable: object, arg: object) -> object:
    """Call ``callable(arg)`` without constructing an argument tuple."""
    ...


def call_twoargs(callable: object, arg0: object, arg1: object) -> object:
    """Call ``callable(arg0, arg1)`` through CPython vectorcall."""
    ...
