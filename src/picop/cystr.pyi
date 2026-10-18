"""Typed C-API helpers for :class:`str` value ops.

Prefer :mod:`picop.cystr` (or starters in :mod:`picop.hot`) for typed string
compares/len/contains; use :mod:`picop.cyunicode` for UTF-8 encode/intern.
Unchecked char accessors are trusted-caller tools — see
:doc:`/user_guide/safety`. Import patterns: :doc:`/user_guide/quickstart`.
"""

def str_or_none(obj: object) -> str | None:
    """Return ``obj`` if exact ``str``, else ``None``."""
    ...

def str_or_empty(obj: object) -> str:
    """Return ``obj`` if truthy exact ``str``, else ``""``."""
    ...

# Preferred public names (0.3 hard trim)

def str_all_alnum_ascii(s: str) -> bool:
    """Return True if ``s`` is non-empty and every code unit is ASCII alnum."""
    ...

def str_all_alpha_ascii(s: str) -> bool:
    """Return True if ``s`` is non-empty and every code unit is ASCII ``A-Za-z``."""
    ...

def str_all_digits(s: str) -> bool:
    """Return True if ``s`` is non-empty and every code unit is ASCII ``0-9``."""
    ...

def str_as_or_empty(obj: object) -> str:
    """Return ``obj`` if it is an exact ``str``, else ``""``."""
    ...

def str_char_at(s: str, i: int) -> int:
    """Return the code point at ``i`` via ``PyUnicode_READ``.

    Notes
    -----
    Unchecked: out-of-bounds is undefined behavior. Bound the index yourself
    before calling.
    """
    ...

def str_concat(a: str, b: str) -> str:
    """Return ``a + b`` via ``PyUnicode_Concat``."""
    ...

def str_concat3(a: str, b: str, c: str) -> str:
    """Return ``a + b + c`` via two ``PyUnicode_Concat`` calls."""
    ...

def str_concat4(a: str, b: str, c: str, d: str) -> str:
    """Return ``a + b + c + d`` via three ``PyUnicode_Concat`` calls."""
    ...

def str_contains(haystack: str, needle: str) -> bool:
    """Return whether ``needle`` is in ``haystack``.

    Notes
    -----
    Uses 1BYTE ``memchr``/``memmem`` or ``Find`` depending on kind.
    """
    ...

def str_endswith(s: str, suffix: str) -> bool:
    """Return whether ``s`` ends with ``suffix``.

    Notes
    -----
    Uses 1BYTE ``memcmp`` or Tailmatch depending on kind.
    """
    ...

def str_first_char(s: str) -> int:
    """Return the first code point via ``PyUnicode_READ``.

    Notes
    -----
    Unchecked: an empty string is undefined behavior.
    """
    ...

def str_is_blank(s: str) -> bool:
    """Return True if every code unit is ASCII whitespace (space/tab/LF/VT/FF/CR)."""
    ...

def str_is_empty(s: str) -> bool:
    """Return True if ``s`` has length 0."""
    ...

def str_is_not(obj: object) -> bool:
    """Return True if ``type(obj) is not str``."""
    ...

def str_is(obj: object) -> bool:
    """Return True if ``type(obj) is str``.

    Notes
    -----
    Same gate as ``str_check_exact`` (N3); alias of ``is_str``.
    """
    ...

def str_last_char(s: str) -> int:
    """Return the last code point via ``PyUnicode_READ``.

    Notes
    -----
    Unchecked: an empty string is undefined behavior.
    """
    ...

def str_none_to_empty(obj: object) -> str:
    """Return ``obj`` if exact ``str``, else ``""``.

    Notes
    -----
    Also yields ``""`` when ``obj is None``.
    """
    ...

def str_not_empty(s: str) -> bool:
    """Return True if ``s`` has non-zero length."""
    ...

def str_startswith(s: str, prefix: str) -> bool:
    """Return whether ``s`` starts with ``prefix``.

    Notes
    -----
    Uses 1BYTE ``memcmp`` or Tailmatch depending on kind.
    """
    ...

def str_eq(a: str, b: str) -> bool:
    """Return whether ``a == b``.

    Notes
    -----
    Uses 1BYTE ``memcmp`` or ``PyUnicode_Compare`` depending on kind.
    """
    ...

def str_cmp(a: str, b: str) -> int:
    """Three-way compare of typed ``str`` values via ``PyUnicode_Compare``.

    Notes
    -----
    Returns ``-1`` / ``0`` / ``1`` for less / equal / greater.
    """
    ...

def str_lt(a: str, b: str) -> bool:
    """Return True if typed ``a < b`` (via ``str_cmp``)."""
    ...

def str_le(a: str, b: str) -> bool:
    """Return True if typed ``a <= b`` (via ``str_cmp``)."""
    ...

def str_gt(a: str, b: str) -> bool:
    """Return True if typed ``a > b`` (via ``str_cmp``)."""
    ...

def str_ge(a: str, b: str) -> bool:
    """Return True if typed ``a >= b`` (via ``str_cmp``)."""
    ...


def str_len(s: str) -> int:
    """Return ``len(s)`` via ``PyUnicode_GET_LENGTH``."""
    ...

def str_ne(a: str, b: str) -> bool:
    """Return whether ``a != b`` (negated ``str_eq``)."""
    ...

def str_check(obj: object) -> bool:
    """Return True if ``obj`` is a :class:`str` or subtype (``PyUnicode_Check``)."""
    ...

def str_check_exact(obj: object) -> bool:
    """Return True if ``type(obj) is str`` (``PyUnicode_CheckExact``).

    Notes
    -----
    Prefer over ``str_is`` / ``is_str`` / ``ucheck_exact`` in check-pair tables
    (N3).
    """
    ...
