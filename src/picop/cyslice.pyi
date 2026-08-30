"""Typed helpers for :class:`slice` construction and index unpacking.

Prefer :mod:`picop.cyslice` when normalizing slice bounds in Cython/typed
paths; otherwise use builtin ``slice``. See :doc:`/user_guide/quickstart` for
import patterns.
"""

# Preferred public names (0.3 hard trim)

def slice_check(p: object) -> bool:
    """Return True if ``p`` is a :class:`slice` (``PySlice_Check``)."""
    ...

def slice_eq(a: slice, b: slice) -> bool:
    """Return True if slices are equal.

    Notes
    -----
    Identity short-circuit plus richcompare.
    """
    ...

def slice_indices_ex(sl: object, length: int) -> tuple[int, int, int, int]:
    """Return ``(start, stop, step, slicelen)`` via ``PySlice_GetIndicesEx``.

    Notes
    -----
    Clips like normal Python slices against ``length``.
    """
    ...

def slice_new(start: object = None, stop: object = None, step: object = None) -> slice:
    """Return ``slice(start, stop, step)`` via ``PySlice_New``."""
    ...

def slice_unpack(sl: object) -> tuple[int, int, int]:
    """Return ``(start, stop, step)`` as C integers via ``PySlice_Unpack``."""
    ...
