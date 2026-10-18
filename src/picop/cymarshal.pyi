"""Marshal dump/load wrapping ``PyMarshal_*``.

Prefer :mod:`marshal` from Python for ordinary use. ``marshal_loads`` on
untrusted data is unsafe — same class as stdlib ``marshal.loads``. See
:doc:`/user_guide/safety` and SAFETY.md.
"""

def marshal_dumps(value: object, version: int = 4) -> object:
    """Serialize ``value`` via ``PyMarshal_WriteObjectToString``."""
    ...

def marshal_loads(data: bytes) -> object:
    """Deserialize marshal bytes via ``PyMarshal_ReadObjectFromString``.

    Notes
    -----
    Untrusted data is unsafe (same class as ``marshal.loads``). Only load
    payloads from a trusted source. See :doc:`/user_guide/safety`.
    """
    ...
