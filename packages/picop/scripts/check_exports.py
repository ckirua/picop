#!/usr/bin/env python3
"""Wave 5/6 export + COMPAT_MAP gates (0.3 hard trim).

Checks:
1. Preferred names in COMPAT_MAP are present on ``picop``.
2. Soft aliases in COMPAT_MAP are **absent** from ``picop`` (hard trim);
   ``__getattr__`` raises ``AttributeError`` with ``soft_alias_removal_hint``.
3. Semantic twins are **not** identity-aliased.
4. Cimport-only modules (tracker Surface) are not imported into ``picop.__init__``.
5. Core ``picop.__all__`` names are importable from ``picop``.

Exit 0 on success.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT_PY = ROOT / "src" / "picop" / "__init__.py"
MODULES = ROOT / "docs" / "modules"

CIMPORT_ONLY_SURFACE = re.compile(
    r"^\|\s*Surface\s*\|\s*cimport only\s*\|", re.I | re.M
)


def cimport_only_modules() -> list[str]:
    out: list[str] = []
    for path in sorted(MODULES.glob("[0-9][0-9][0-9]_*.md")):
        text = path.read_text(encoding="utf-8")
        if CIMPORT_ONLY_SURFACE.search(text):
            # stem like 010_cyerr → cyerr
            out.append(path.stem.split("_", 1)[1])
    return out


def init_imported_modules() -> set[str]:
    """Submodule names imported in ``__init__.py`` (``from .cyfoo import``)."""
    tree = ast.parse(INIT_PY.read_text(encoding="utf-8"), filename=str(INIT_PY))
    mods: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            # relative: .cyerr → cyerr
            mods.add(node.module.lstrip("."))
    return mods


def main() -> int:
    # Import after path is the installed/editable package
    import picop
    from picop.compat import COMPAT_MAP, SEMANTIC_TWINS, soft_alias_removal_hint

    errors: list[str] = []

    # 1) Preferred names present
    for soft, pref in sorted(COMPAT_MAP.items()):
        if not hasattr(picop, pref):
            errors.append(f"COMPAT preferred missing on picop: {pref} (from {soft})")

    # 2) Soft aliases removed from root; __getattr__ hints
    for soft in sorted(COMPAT_MAP):
        # Use getattr to exercise __getattr__ (hasattr may swallow AttributeError)
        try:
            getattr(picop, soft)
        except AttributeError as exc:
            hint = soft_alias_removal_hint(soft)
            if hint is None:
                errors.append(f"soft {soft}: no removal hint in compat")
            elif hint not in str(exc):
                errors.append(
                    f"soft {soft}: AttributeError missing hint text: {exc!r}"
                )
        else:
            errors.append(f"COMPAT soft still on picop after 0.3 trim: {soft}")

    # 3) Semantic twins must not be identity
    for a, b in SEMANTIC_TWINS:
        if not (hasattr(picop, a) and hasattr(picop, b)):
            errors.append(f"twin missing: {a} / {b}")
            continue
        if getattr(picop, a) is getattr(picop, b):
            errors.append(f"semantic twin collapsed to identity: {a} is {b}")

    # 4) cimport-only modules must not be Python-imported in __init__.py
    imported = init_imported_modules()
    for mod in cimport_only_modules():
        if mod in imported:
            errors.append(f"cimport-only module imported in __init__.py: {mod}")

    # 5) Core __all__ importable
    for name in picop.__all__:
        if not hasattr(picop, name):
            errors.append(f"__all__ name missing: {name}")

    if errors:
        print("check_exports FAIL:")
        for e in errors:
            print(" -", e)
        return 1

    print(
        f"check_exports OK: {len(COMPAT_MAP)} soft aliases trimmed, "
        f"{len(SEMANTIC_TWINS)} twins, "
        f"{len(cimport_only_modules())} cimport-only modules clean, "
        f"{len(picop.__all__)} Core __all__"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
