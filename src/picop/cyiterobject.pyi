"""Sequence and callable iterator type checks via ``PySeqIter_*`` /
``PyCallIter_*``.

Prefer :func:`iter` / iterator protocol from Python unless you need exact
iterator-kind checks. Tier A losers remain ``cpdef`` and carry a parity note in
the stub. See :doc:`/user_guide/quickstart`.
"""

def seqiter_check(op: object) -> bool:
    """Return True if ``op`` is a sequence iterator (``PySeqIter_Check``)."""
    ...

def calliter_check(op: object) -> bool:
    """Return True if ``op`` is a callable iterator (``PyCallIter_Check``)."""
    ...

def calliter_new(callable_: object, sentinel: object) -> object:
    """Return a call iterator for ``callable_`` stopping at ``sentinel`` (``PyCallIter_New``)."""
    ...

def seqiter_new(seq: object) -> object:
    """Return a sequence iterator for ``seq`` (``PySequence_GetIterator``).

    Notes
    -----
    Slower than the plain-Python equivalent ``iter(x)`` (Tier A 1.34x); the typed
    Cython call site.
    """
    ...
