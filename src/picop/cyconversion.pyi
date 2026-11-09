"""OS string/double conversion helpers wrapping ``PyOS_*``.

Prefer Python ``str``/``float`` parsing unless you need C-string compare or
``PyOS_string_to_double`` semantics. Inputs are ``bytes``, not ``str``. See
:doc:`/user_guide/safety`.
"""

def conv_stricmp(s1: bytes, s2: bytes) -> int:
    """Case-insensitive C-string compare via ``PyOS_stricmp``.

    Notes
    -----
    ``s1`` / ``s2`` must be ``bytes``, not ``str``.
    """
    ...

def conv_strnicmp(s1: bytes, s2: bytes, size: int) -> int:
    """Case-insensitive compare of at most ``size`` bytes via ``PyOS_strnicmp``.

    Notes
    -----
    ``s1`` / ``s2`` must be ``bytes``, not ``str``.
    """
    ...

def conv_cstr_to_double(s: bytes) -> float:
    """Parse ``s`` as a C double via ``PyOS_string_to_double``.

    Notes
    -----
    ``s`` must be ``bytes`` with no surrounding whitespace. Alias of
    ``conv_string_to_double`` (prefer ``*_cstr`` naming). See
    :doc:`/user_guide/safety`.
    """
    ...
