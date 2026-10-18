#!/usr/bin/env python3
"""Fail if any public ``.pyi`` ``def`` / ``@property`` / documented dunder lacks a docstring.

Scans ``src/picop/**/*.pyi``. Private names (leading ``_`` except dunders) may be
allowlisted via ``ALLOW_UNDOCUMENTED`` if needed. Exit 0 on success.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYI_ROOT = ROOT / "src" / "picop"

# Fully-qualified ``module:Class.member`` or ``module:func`` names that may lack docs.
ALLOW_UNDOCUMENTED: frozenset[str] = frozenset()

FORBIDDEN_SECTIONS = (
    "Args:",
    "Arguments:",
    "Parameters:",
    "Returns:",
    "Return:",
    "Raises:",
    "Yields:",
)


def _is_public_name(name: str) -> bool:
    if name.startswith("__") and name.endswith("__"):
        return True
    return not name.startswith("_")


def _qual(mod: str, *parts: str) -> str:
    return f"{mod}:{'.'.join(parts)}"


def _check_doc(doc: str | None, qual: str, errors: list[str]) -> None:
    if not doc or not doc.strip():
        errors.append(f"missing docstring: {qual}")
        return
    for marker in FORBIDDEN_SECTIONS:
        if marker in doc:
            errors.append(f"forbidden section {marker!r} in {qual}")


def check_file(path: Path) -> list[str]:
    rel = path.relative_to(PYI_ROOT)
    mod = ".".join(rel.with_suffix("").parts)
    if mod.endswith("._uuid"):
        mod = "uuid"
    text = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        return [f"syntax error in {path}: {exc}"]

    errors: list[str] = []
    mod_doc = ast.get_docstring(tree)
    if not mod_doc or not mod_doc.strip():
        errors.append(f"missing module docstring: {path.relative_to(ROOT)}")

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not _is_public_name(node.name):
                continue
            qual = _qual(mod, node.name)
            if qual in ALLOW_UNDOCUMENTED:
                continue
            _check_doc(ast.get_docstring(node), qual, errors)
        elif isinstance(node, ast.ClassDef):
            if not _is_public_name(node.name):
                continue
            cqual = _qual(mod, node.name)
            if cqual not in ALLOW_UNDOCUMENTED:
                _check_doc(ast.get_docstring(node), cqual, errors)
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not _is_public_name(child.name):
                        continue
                    mqual = _qual(mod, node.name, child.name)
                    if mqual in ALLOW_UNDOCUMENTED:
                        continue
                    _check_doc(ast.get_docstring(child), mqual, errors)
    return errors


def main() -> int:
    paths = sorted(PYI_ROOT.rglob("*.pyi"))
    if not paths:
        print("no .pyi files found", file=sys.stderr)
        return 1
    errors: list[str] = []
    for path in paths:
        errors.extend(check_file(path))
    if errors:
        print(f"check_pyi_docstrings: {len(errors)} issue(s)", file=sys.stderr)
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    print(f"check_pyi_docstrings: ok ({len(paths)} stubs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
