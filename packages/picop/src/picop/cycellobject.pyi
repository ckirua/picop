"""Cell-object construction and access wrapping ``PyCell_*``.

Prefer closure introspection from Python unless you need C-API cell get/set
on a known cell. Status-int setters return ``0`` on success. See
:doc:`/user_guide/quickstart`.
"""

def cell_check(ob: object) -> bool:
    """Return True if ``ob`` is a cell object (``PyCell_Check``)."""
    ...

def cell_new(ob: object) -> object:
    """Return a new cell containing ``ob`` (``PyCell_New``; ``ob`` may be ``None``)."""
    ...

def cell_get(cell: object) -> object:
    """Return the contents of ``cell`` via ``PyCell_Get``."""
    ...

def cell_set(cell: object, value: object) -> int:
    """Set the contents of ``cell`` via ``PyCell_Set``.

    Notes
    -----
    Returns ``0`` on success; errors raise — do not use the status as a bool.
    """
    ...

def cell_eq(a: object, b: object) -> bool:
    """Return True if cell contents compare equal (not identity; empty↔empty True)."""
    ...
