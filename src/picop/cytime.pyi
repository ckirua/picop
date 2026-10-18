"""Monotonic and perf-counter clocks via ``PyTime_*``.

Prefer :func:`time.monotonic` / :func:`time.perf_counter` from Python unless
you need the C-API clocks on a hot path. Tier A losers remain ``cpdef`` but
are omitted from stubs. See :doc:`/user_guide/quickstart`.
"""

def time_monotonic() -> float:
    """Return monotonic seconds via ``PyTime_Monotonic``."""
    ...

def time_perf_counter() -> float:
    """Return perf-counter seconds via ``PyTime_PerfCounter``."""
    ...
