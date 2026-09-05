"""Weak-reference construction and checks wrapping ``PyWeakref_*``.

Prefer :mod:`weakref` from Python unless you need C-API construction on a
known referent. See :doc:`/user_guide/quickstart`.
"""

def weakref_check(ob: object) -> bool:
    """Return True if ``ob`` is a weak reference or proxy."""
    ...

def weakref_check_ref(ob: object) -> bool:
    """Return True if ``ob`` is a weak referent (``PyWeakref_CheckRef``)."""
    ...

def weakref_check_proxy(ob: object) -> bool:
    """Return True if ``ob`` is a weak proxy."""
    ...

def weakref_new_ref(ob: object, callback: object = None) -> object:
    """Return a weak reference via ``PyWeakref_NewRef``."""
    ...

def weakref_new_proxy(ob: object, callback: object = None) -> object:
    """Return a weak proxy via ``PyWeakref_NewProxy``."""
    ...

def weakref_get_object(ref: object) -> object:
    """Return the referent of ``ref``, or ``None`` if dead (owned ref)."""
    ...

def weakref_eq(a: object, b: object) -> bool:
    """Return True if weakrefs equal (referent ``==`` when alive; identity if dead)."""
    ...
