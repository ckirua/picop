"""Fast traceback-object readers (CPython 3.8+)."""

def tb_check(tb: object) -> bool:
    """Return whether ``tb`` is a traceback object."""
    ...

def tb_next(tb: object) -> object:
    """Return the next traceback in ``tb``'s chain, or ``None``."""
    ...

def tb_frame(tb: object) -> object:
    """Return the frame associated with ``tb``."""
    ...

def tb_lineno(tb: object) -> int:
    """Return the source line associated with ``tb``."""
    ...

def tb_lasti(tb: object) -> int:
    """Return the bytecode offset associated with ``tb``."""
    ...

def tb_depth(tb: object) -> int:
    """Return the number of traceback entries beginning with ``tb``."""
    ...
