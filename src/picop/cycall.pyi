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
    Mixed Tier A parity: 1.01x (3.14), 1.07x (3.14t), 0.97x (3.15), 0.97x (3.15t);
    the typed Cython call site.
    """
    ...


def call_onearg(callable: object, arg: object) -> object:
    """Call ``callable(arg)`` without constructing an argument tuple."""
    ...


def call_twoargs(callable: object, arg0: object, arg1: object) -> object:
    """Call ``callable(arg0, arg1)`` through CPython vectorcall.

    Notes
    -----
    Mixed Tier A parity: 1.09x (3.14), 1.03x (3.14t), 1.02x (3.15), 1.03x (3.15t);
    the typed Cython call site.
    """
    ...
