"""Capsule type checks wrapping ``PyCapsule_*``.

Prefer :mod:`ctypes` / extension APIs that expose capsules unless you need
exact-type or name validation on a known capsule. Capsule names take
``bytes``. See :doc:`/user_guide/safety`.
"""

def capsule_check_exact(o: object) -> bool:
    """Return True if ``type(o) is types.CapsuleType`` (``PyCapsule_CheckExact``)."""
    ...

def capsule_is_valid(capsule: object, name: bytes) -> bool:
    """Return True if ``capsule`` is a valid capsule named ``name``.

    Notes
    -----
    ``name`` must be ``bytes``, not ``str``.
    """
    ...

def capsule_eq(a: object, b: object) -> bool:
    """Return True if ``a is b`` (capsule identity; not pointer/name content)."""
    ...
