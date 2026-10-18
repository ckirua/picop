"""Thin C-API wrappers for the cyclic garbage collector.

Prefer :mod:`picop.cygc` when you need GC enable/disable/collect from typed
hot paths; otherwise use :mod:`gc`. See :doc:`/user_guide/quickstart` for
import patterns.
"""

def gc_collect() -> int:
    """Run a full GC collection via ``PyGC_Collect``; return unreachable count."""
    ...

def gc_is_enabled() -> bool:
    """Return whether automatic GC is enabled via ``PyGC_IsEnabled``."""
    ...

def gc_enable() -> int:
    """Enable automatic GC via ``PyGC_Enable``; return the prior enabled flag."""
    ...

def gc_disable() -> int:
    """Disable automatic GC via ``PyGC_Disable``; return the prior enabled flag."""
    ...
