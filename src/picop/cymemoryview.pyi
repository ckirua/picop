"""Typed helpers for :class:`memoryview`.

Prefer :mod:`picop.cymemoryview` (or starters in :mod:`picop.hot`) for typed
view equality and contiguous views. See :doc:`/user_guide/quickstart` for
import patterns.
"""

# Preferred public names (0.3 hard trim)

def memoryview_check(p: object) -> bool:
    """Return True if ``p`` is a :class:`memoryview` (``PyMemoryView_Check``)."""
    ...

def memoryview_eq(a: memoryview, b: memoryview) -> bool:
    """Return True if views are equal.

    Notes
    -----
    C-contiguous buffers use a ``memcmp`` fast path; otherwise falls back to
    richcompare.
    """
    ...

def memoryview_ne(a: memoryview, b: memoryview) -> bool:
    """Return True if views differ.

    Notes
    -----
    Inverse of ``memoryview_eq``; same contig/richcompare rules.
    """
    ...

def memoryview_from_object(obj: object) -> memoryview:
    """Return ``memoryview(obj)`` via ``PyMemoryView_FromObject``."""
    ...

def memoryview_get_contiguous(obj: object, buffertype: int = ..., order: str = "C") -> memoryview:
    """Return a contiguous memoryview of ``obj`` via ``PyMemoryView_GetContiguous``.

    Notes
    -----
    ``order`` is ``C``, ``F``, or ``A``.
    """
    ...
