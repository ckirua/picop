# cython: freethreading_compatible=True
# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
"""
Thread and interpreter lifecycle helpers.

The lock/GIL slice stays cimport-only; ``interpreter_guard`` (Order 077) is
the public context manager.
"""

cdef class InterpreterGuard:
    """Finalization guard for the current interpreter (CPython 3.15+).

    Acquired on creation, closed on ``__exit__`` or deallocation. Re-open
    after exit is a no-op (the guard is already closed). Raises
    ``RuntimeError`` on CPython < 3.15; test ``guards_supported()`` first.
    """

    cdef void *_guard

    def __cinit__(self) -> None:
        self._guard = guard_from_current()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        guard_close(self._guard)
        self._guard = NULL
        return False

    def __dealloc__(self) -> None:
        guard_close(self._guard)
        self._guard = NULL


cpdef guards_supported():
    """Return True when CPython provides interpreter guards (3.15+)."""
    return guards_enabled() == 1


cpdef interpreter_guard():
    """Context manager preventing interpreter finalization (CPython 3.15+)."""
    return InterpreterGuard()
