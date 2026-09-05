"""Buffer-protocol helpers for objects that expose a buffer.

Prefer :mod:`picop.cybuffer` when comparing or copying buffer views without a
known concrete type; use typed :mod:`picop.cybytes` /
:mod:`picop.cymemoryview` when possible. See :doc:`/user_guide/quickstart` for
import patterns.
"""

def buf_check(obj: object) -> bool:
    """Return True if ``obj`` supports the buffer protocol (``PyObject_CheckBuffer``)."""
    ...

def buf_copy_data(dest: object, src: object) -> int:
    """Copy buffer data from ``src`` into writable ``dest`` via ``PyObject_CopyData``.

    Notes
    -----
    Returns ``0`` on success and ``-1`` on error; errors raise. Do not use the
    status int as a bool.
    """
    ...

def buf_eq(a: object, b: object) -> bool:
    """Return True if buffer-protocol views are equal.

    Notes
    -----
    C-contiguous buffers use ``memcmp``; otherwise memoryview richcompare.
    Format/size mismatch yields ``False``.
    """
    ...
