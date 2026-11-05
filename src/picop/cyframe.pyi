"""Fast frame-object accessors (CPython 3.10+)."""

def frame_check(frame: object) -> bool:
    """Return whether ``frame`` is a frame object."""
    ...

def frame_lineno(frame: object) -> int:
    """Return the current source line for ``frame``."""
    ...

def frame_lasti(frame: object) -> int:
    """Return the last instruction offset for ``frame``."""
    ...

def frame_code(frame: object) -> object:
    """Return the code object executed by ``frame``."""
    ...

def frame_back(frame: object) -> object | None:
    """Return the previous frame, or None when there is none."""
    ...

def frame_locals(frame: object) -> object:
    """Return the live local namespace for ``frame``.

    Notes
    -----
    Function frames expose a ``FrameLocalsProxy``; module frames expose a dict.
    """
    ...

def frame_globals(frame: object) -> object:
    """Return the global namespace for ``frame``."""
    ...

def frame_builtins(frame: object) -> object:
    """Return the builtins namespace for ``frame``."""
    ...

def frame_generator(frame: object) -> object | None:
    """Return the generator or coroutine owning ``frame``, if any."""
    ...

def frame_var(frame: object, name: str) -> object:
    """Return the value of ``name`` in ``frame``."""
    ...

def frame_var_cstr(frame: object, name: bytes) -> object:
    """Return the value of the NUL-terminated name in ``frame``.

    Notes
    -----
    Pass ``name`` as bytes; embedded NUL bytes terminate the C string.
    """
    ...
