"""Monotonic and perf-counter clocks via ``PyTime_*``.

Prefer :func:`time.monotonic` / :func:`time.perf_counter` from Python unless
you need the C-API clocks on a hot path. Tier A losers remain ``cpdef`` and
carry a parity note in the stub. See :doc:`/user_guide/quickstart`.
"""

def time_monotonic() -> float:
    """Return monotonic seconds via ``PyTime_Monotonic``.

    Notes
    -----
    Slower than the plain-Python equivalent ``time.monotonic`` (Tier A 1.03x); the
    typed Cython call site.
    """
    ...

def time_perf_counter() -> float:
    """Return perf-counter seconds via ``PyTime_PerfCounter``.

    Notes
    -----
    Slower than the plain-Python equivalent ``time.perf_counter`` (Tier A 1.03x);
    the typed Cython call site.
    """
    ...

def time_wall() -> float:
    """Return the wall-clock time in seconds (``PyTime`` wall clock).

    Notes
    -----
    Slower than the plain-Python equivalent ``time.time`` (Tier A 1.06x); the typed
    Cython call site.
    """
    ...
