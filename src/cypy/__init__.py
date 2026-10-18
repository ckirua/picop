"""Deprecated import alias for :mod:`picop` (removal planned in 3.0).

Prefer::

    from picop.hot import bytes_len
    from picop cimport bytes_len

``pip install picop`` — the distribution name is already ``picop``.
"""

from __future__ import annotations

import importlib
import pkgutil
import sys
import warnings

warnings.warn(
    "The 'cypy' import package is deprecated; use 'picop' instead "
    "(removal planned in picop 3.0). pip install name is already 'picop'.",
    DeprecationWarning,
    stacklevel=2,
)

import picop as _picop
from picop import *  # noqa: F403
from picop import __all__, __version__  # noqa: F401

# Re-export soft-alias machinery under the deprecated name.
from picop.compat import (  # noqa: F401
    COMPAT_MAP,
    SEMANTIC_TWINS,
    soft_alias_removal_hint,
)


def _mirror_picop_modules() -> None:
    """Map ``cypy.*`` → already-loaded ``picop.*`` modules in ``sys.modules``."""
    # Import leaf extension modules that picop.__init__ already pulled in, plus
    # pure-Python facades / uuid, so ``import cypy.hot`` resolves via sys.modules.
    for info in pkgutil.walk_packages(_picop.__path__, prefix="picop."):
        name = info.name
        if name.endswith(".__about__"):
            continue
        try:
            importlib.import_module(name)
        except Exception:
            # Optional / cimport-only style modules may fail to import as Python.
            continue
    for name, mod in list(sys.modules.items()):
        if name == "picop" or name.startswith("picop."):
            alias = "cypy" + name[len("picop") :]
            sys.modules.setdefault(alias, mod)


_mirror_picop_modules()


def __getattr__(name: str):
    # Prefer picop's own soft-alias __getattr__ / attributes.
    try:
        return getattr(_picop, name)
    except AttributeError:
        pass
    try:
        mod = importlib.import_module(f"picop.{name}")
    except ModuleNotFoundError as exc:
        raise AttributeError(name) from exc
    sys.modules.setdefault(f"cypy.{name}", mod)
    return mod
