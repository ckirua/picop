"""Fast code-object readers (CPython 3.11+)."""

def code_check(code: object) -> bool:
    """Return whether ``code`` is a code object."""
    ...

def code_name(code: object) -> object:
    """Return the name of ``code``."""
    ...

def code_qualname(code: object) -> object:
    """Return the qualified name of ``code``."""
    ...

def code_filename(code: object) -> object:
    """Return the filename associated with ``code``."""
    ...

def code_firstlineno(code: object) -> int:
    """Return the first source line of ``code``."""
    ...

def code_argcount(code: object) -> int:
    """Return the number of positional arguments accepted by ``code``."""
    ...

def code_posonlyargcount(code: object) -> int:
    """Return the number of positional-only arguments accepted by ``code``."""
    ...

def code_kwonlyargcount(code: object) -> int:
    """Return the number of keyword-only arguments accepted by ``code``."""
    ...

def code_consts(code: object) -> object:
    """Return the constants referenced by ``code``."""
    ...

def code_names(code: object) -> object:
    """Return the names referenced by ``code``."""
    ...

def code_code(code: object) -> bytes:
    """Return the bytecode representation of ``code``."""
    ...

def code_varnames(code: object) -> object:
    """Return the local variable names of ``code``."""
    ...

def code_cellvars(code: object) -> object:
    """Return the cell variable names of ``code``."""
    ...

def code_freevars(code: object) -> object:
    """Return the free variable names of ``code``."""
    ...

def code_addr2line(code: object, addr: int) -> int:
    """Return the source line corresponding to bytecode offset ``addr``."""
    ...
