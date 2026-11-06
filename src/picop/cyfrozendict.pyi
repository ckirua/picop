"""Typed checks and constructors for :class:`frozendict` (CPython 3.15+).

``frozendict`` is **not** a ``dict`` subclass, so ``dict_check`` /
``dict_check_exact`` are ``False`` for it. Use the ``anydict_*`` helpers when a
value may be either. On CPython 3.14 the checks answer ``False`` and the
constructors raise ``NotImplementedError`` — never a mutable ``dict``.
"""

def frozendict_check(obj: object) -> bool:
    """Return True if ``obj`` is a frozendict or a frozendict subtype."""
    ...

def frozendict_check_exact(obj: object) -> bool:
    """Return True if ``obj`` is exactly a frozendict (subtypes excluded)."""
    ...

def anydict_check(obj: object) -> bool:
    """Return True if ``obj`` is a dict or a frozendict (subtypes included).

    Notes
    -----
    mirrors ``PyAnyDict_Check``; on 3.14 this is ``dict_check``.
    """
    ...

def anydict_check_exact(obj: object) -> bool:
    """Return True if ``obj`` is exactly a dict or exactly a frozendict.

    Notes
    -----
    ``dict`` subclasses such as ``defaultdict`` are False.
    """
    ...

def frozendict_new(iterable: object) -> object:
    """Return a new frozendict built from an iterable.

    Notes
    -----
    Mixed Tier A parity: 0.54x (from frozendict), 1.04x (from dict (4 items)); the
    3.15 ``frozendict`` bridge.

    ``None`` is not iterable — use ``frozendict_empty()`` for the
    no-iterable path. Passing an existing frozendict returns **the same
    object** with an incremented reference, not a copy. Raises
    ``NotImplementedError`` on 3.14.
    """
    ...

def frozendict_empty() -> object:
    """Return an empty frozendict without building an iterable.

    Notes
    -----
    raises ``NotImplementedError`` on 3.14.
    """
    ...

def anydict_len(obj: object) -> int:
    """Return the entry count of a dict or frozendict.

    Notes
    -----
    raises ``TypeError`` for anything else; the read uses the
    ``PyDict_GET_SIZE`` layout shared by dict and frozendict.
    """
    ...
