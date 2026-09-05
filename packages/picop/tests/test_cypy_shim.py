"""Deprecated ``cypy`` soft-shim identity and warning checks."""

from __future__ import annotations

import warnings

import picop


def test_import_cypy_emits_deprecation_warning() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        # Force a fresh warning even if cypy was already imported elsewhere.
        import importlib
        import sys

        sys.modules.pop("cypy", None)
        import cypy  # noqa: F401

        importlib.reload(cypy)

    msgs = [str(w.message) for w in caught if issubclass(w.category, DeprecationWarning)]
    assert msgs, "expected DeprecationWarning on import cypy"
    assert any("deprecated" in m.lower() and "picop" in m.lower() for m in msgs)


def test_cypy_hot_is_picop_hot() -> None:
    import cypy
    import picop.hot
    import cypy.hot

    assert cypy.hot is picop.hot


def test_cypy_root_name_identity() -> None:
    import cypy

    assert cypy.bytes_len is picop.bytes_len


def test_cypy_version_matches_picop() -> None:
    import cypy

    assert cypy.__version__ == picop.__version__
