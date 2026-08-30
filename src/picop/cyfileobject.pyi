"""File-object helpers wrapping ``PyFile_*``.

Prefer stdlib ``open`` / ``io`` from Python unless you need C-API fd wrapping
or write helpers. ``*_cstr`` / mode strings take ``bytes``, not ``str``. See
:doc:`/user_guide/safety`.
"""

def file_from_fd(fd: int, name: bytes, mode: bytes, buffering: int = -1, encoding: bytes | None = None, errors: bytes | None = None, newline: bytes | None = None, closefd: int = 1) -> object:
    """Wrap OS ``fd`` as a Python file via ``PyFile_FromFd``.

    Notes
    -----
    ``name`` / ``mode`` / optional codec strings must be ``bytes``, not ``str``.
    """
    ...

def file_getline(p: object, n: int = -1) -> object:
    """Read a line from file ``p`` via ``PyFile_GetLine``."""
    ...

def file_write_object(obj: object, p: object, flags: int = 0) -> int:
    """Write ``obj`` to file ``p`` via ``PyFile_WriteObject``.

    Notes
    -----
    Returns ``0`` on success; errors raise — do not use the status as a bool.
    """
    ...

def file_write_cstr(s: bytes, p: object) -> int:
    """Write C string ``s`` to file ``p`` via ``PyFile_WriteString``.

    Notes
    -----
    ``s`` must be ``bytes``, not ``str``. Returns ``0`` on success; errors
    raise — do not use the status as a bool. Alias of ``file_write_string``.
    """
    ...
