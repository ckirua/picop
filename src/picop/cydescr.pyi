"""Descriptor introspection via ``PyDescr_IsData``.

Prefer :mod:`inspect` / attribute protocol from Python unless you need a
C-API data-descriptor check. See :doc:`/user_guide/quickstart`.
"""

def descr_is_data(descr: object) -> bool:
    """Return True if ``descr`` is a data descriptor (``PyDescr_IsData``)."""
    ...
