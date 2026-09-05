"""Module creation, import, and constant-registration helpers via ``PyModule_*``.

Prefer stdlib ``importlib`` / module attributes from Python unless you need
C-API module construction. ``*_cstr`` / ``bytes`` names are C strings, not
``str``. See :doc:`/user_guide/safety`.
"""

def mod_check(p: object) -> bool:
    """Return True if ``p`` is a module or subtype (``PyModule_Check``)."""
    ...

def mod_check_exact(p: object) -> bool:
    """Return True if ``type(p) is types.ModuleType`` (``PyModule_CheckExact``)."""
    ...

def mod_eq(a: object, b: object) -> bool:
    """Return True if ``a is b`` (module-object identity; CPython ``object.__eq__``)."""
    ...

def mod_new(name: bytes) -> object:
    """Return a new module named ``name`` via ``PyModule_New``.

    Notes
    -----
    ``name`` must be ``bytes``, not ``str``.
    """
    ...

def mod_new_object(name: object) -> object:
    """Return a new module named ``name`` via ``PyModule_NewObject``."""
    ...

def mod_get_name(module: object) -> object:
    """Return ``module.__name__`` via ``PyModule_GetNameObject``."""
    ...

def mod_get_filename(module: object) -> object:
    """Return ``module.__file__`` via ``PyModule_GetFilenameObject``."""
    ...

def mod_add_object_ref(module: object, name: bytes, value: object) -> int:
    """Add ``value`` as ``name`` without stealing the reference (``PyModule_AddObjectRef``).

    Notes
    -----
    ``name`` must be ``bytes``. Returns ``0`` on success; errors raise — do not
    use the status as a bool.
    """
    ...

def mod_add_int(module: object, name: bytes, value: int) -> int:
    """Add integer constant ``name`` via ``PyModule_AddIntConstant``.

    Notes
    -----
    ``name`` must be ``bytes``. Returns ``0`` on success; errors raise — do not
    use the status as a bool.
    """
    ...

def mod_import(name: bytes) -> object:
    """Import module ``name`` via ``PyImport_ImportModule``.

    Notes
    -----
    ``name`` must be ``bytes``, not ``str``.
    """
    ...

def mod_import_object(name: object) -> object:
    """Import module ``name`` via ``PyImport_Import``."""
    ...

def mod_reload(m: object) -> object:
    """Reload module ``m`` via ``PyImport_ReloadModule``."""
    ...

def mod_magic_number() -> int:
    """Return the ``.pyc`` magic number via ``PyImport_GetMagicNumber``."""
    ...

def mod_add_cstr(module: object, name: bytes, value: bytes) -> int:
    """Add string constant ``name`` via ``PyModule_AddStringConstant``.

    Notes
    -----
    ``name`` and ``value`` must be ``bytes``, not ``str``. Returns ``0`` on
    success; errors raise — do not use the status as a bool. Alias of
    ``mod_add_string`` (prefer ``*_cstr`` naming).
    """
    ...
