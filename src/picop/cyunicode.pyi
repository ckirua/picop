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

class UnicodeWriter:
    """Build a string incrementally with CPython's Unicode writer."""

    def __init__(self, max_size: int = 0) -> None:
        """Initialize an empty string writer."""
        ...

    def write(self, text: object) -> None:
        """Append a string to the writer."""
        ...

    def write_char(self, ch: int) -> None:
        """Append a Unicode code point."""
        ...

    def write_ascii(self, text: str) -> None:
        """Append ASCII text."""
        ...

    def write_repr(self, obj: object) -> None:
        """Append the representation of an object."""
        ...

    def write_substring(self, text: str, start: int = 0, end: int = -1) -> None:
        """Append a substring."""
        ...

    def write_utf8(self, data: bytes) -> None:
        """Append UTF-8 encoded bytes."""
        ...

    def finish(self) -> str:
        """Finish writing and return the built string."""
        ...

    def discard(self) -> None:
        """Discard the writer buffer."""
        ...

    def __enter__(self) -> UnicodeWriter:
        """Return this writer."""
        ...

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        """Discard an unfinished writer when leaving the context."""
        ...
