"""Typed checks and constructors for :class:`frozendict` (CPython 3.15+).

``frozendict`` is **not** a subclass of ``dict``, so ``dict_check`` /
``dict_check_exact`` are ``False`` for it. Use the ``anydict_*`` helpers when
a value may be either. On CPython 3.14 the checks answer ``False`` and the
constructors raise :exception:`NotImplementedError`. See
:doc:`/user_guide/quickstart` for import patterns.
"""

def frozendict_check(obj: object) -> bool:
    """Return True if obj is a frozendict or a frozendict subtype.

    Notes
    -----
    ``frozendict`` is a standalone type, not a ``dict`` subclass — a frozendict
    is never ``dict_check``-true.
    """
    ...

def frozendict_check_exact(obj: object) -> bool:
    """Return True if obj is exactly a frozendict (no subclasses possible)."""
    ...

def anydict_check(obj: object) -> bool:
    """Return True if obj is a dict or a frozendict (or a subtype of either).

    Notes
    -----
    Mirrors ``PyAnyDict_Check``. On 3.14 this is ``dict_check``.
    """
    ...

def anydict_check_exact(obj: object) -> bool:
    """Return True if obj is exactly a dict or exactly a frozendict.

    Notes
    -----
    Mirrors ``PyAnyDict_CheckExact``; ``dict`` subclasses (e.g. ``defaultdict``)
    are False.
    """
    ...

def frozendict_new(iterable: object) -> frozendict:
    """Return a new frozendict built from *iterable*.

    Notes
    -----
    Same semantics as ``frozendict(iterable)``: a mapping, an iterable of
    key/value pairs, or another frozendict. ``PyDict_Copy`` / ``PyDict_Merge``
    do **not** accept a frozendict — copy through this helper. Raises
    :exception:`NotImplementedError` on CPython 3.14.
    """
    ...

def frozendict_empty() -> frozendict:
    """Return an empty frozendict (``PyFrozenDict_New(NULL)``, no iterable).

    Raises
    ------
    NotImplementedError
        On CPython 3.14.
    """
    ...

def anydict_len(obj: object) -> int:
    """Return the number of entries in a dict or frozendict.

    Notes
    -----
    Raises :exception:`TypeError` when *obj* is neither; the read path uses the
    unchecked ``PyDict_GET_SIZE`` layout shared by dict and frozendict.
    """
    ...
