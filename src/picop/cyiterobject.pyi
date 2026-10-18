"""Sequence and callable iterator type checks via ``PySeqIter_*`` / ``PyCallIter_*``.

Prefer :func:`iter` / iterator protocol from Python unless you need exact
iterator-kind checks. Tier A losers remain ``cpdef`` but are omitted from
stubs. See :doc:`/user_guide/quickstart`.
"""

def seqiter_check(op: object) -> bool:
    """Return True if ``op`` is a sequence iterator (``PySeqIter_Check``)."""
    ...

def calliter_check(op: object) -> bool:
    """Return True if ``op`` is a callable iterator (``PyCallIter_Check``)."""
    ...
