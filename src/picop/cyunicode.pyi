"""UTF-8 encode and intern helpers for :class:`str`.

Prefer :mod:`picop.cyunicode` for owning UTF-8 bytes and interning; use
:mod:`picop.cystr` for typed value ops (eq/len/contains). Borrowed UTF-8
pointers are cimport-only — see :doc:`/user_guide/safety`. Import patterns:
:doc:`/user_guide/quickstart`.
"""

def uutf8_bytes(s: str) -> bytes:
    """Return owning UTF-8 ``bytes`` for ``s`` via ``PyUnicode_AsUTF8String``.

    Notes
    -----
    Owning copy — safe to keep past the lifetime of ``s``. Prefer this over
    borrowed ``uutf8`` (cimport-only) when you need a durable value.
    """
    ...

def uintern(s: str) -> str:
    """Intern ``s`` via ``PyUnicode_InternInPlace`` and return the canonical instance."""
    ...

def unicode_eq(a: str, b: str) -> bool:
    """Return True if ``a == b``.

    Notes
    -----
    Thin alias of ``str_eq`` with the same semantics; prefer ``str_eq`` from
    :mod:`picop.cystr` on value-op hot paths.
    """
    ...
