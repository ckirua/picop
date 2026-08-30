"""Sphinx configuration for the public picop documentation site."""

from __future__ import annotations

import ast
import importlib.metadata
import sys
from pathlib import Path

# -- Paths --------------------------------------------------------------------

DOC_ROOT = Path(__file__).resolve().parent
REPO_ROOT = DOC_ROOT.parent
PACKAGE_SRC = REPO_ROOT / "src" / "picop"

sys.path.insert(0, str(REPO_ROOT / "src"))

# -- Project ------------------------------------------------------------------

project = "picop"
copyright = "2026, ckirua"
author = "ckirua"

try:
    version = release = importlib.metadata.version("picop")
except importlib.metadata.PackageNotFoundError:
    from picop.__about__ import __version__ as version  # type: ignore[no-redef]

    release = version

# -- General ------------------------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "linkify",
    "substitution",
    "tasklist",
]

autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource",
}
autodoc_typehints = "description"
autodoc_member_order = "bysource"
napoleon_google_docstring = True
napoleon_numpy_docstring = True
always_document_param_types = True
typehints_defaults = "comma"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "cython": ("https://cython.readthedocs.io/en/latest/", None),
}

# -- HTML ---------------------------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_title = "picop"
html_short_title = "picop"
html_baseurl = "https://ckirua.github.io/picop/"

html_theme_options = {
    "github_url": "https://github.com/ckirua/picop",
    "use_edit_page_button": False,
    "show_toc_level": 2,
    "navigation_with_keys": True,
    "logo": {
        "text": "picop",
    },
    # Stub for a future multi-version Pages layout; v1 ships a single latest build.
    "switcher": {
        "json_url": "https://ckirua.github.io/picop/_static/switcher.json",
        "version_match": release,
    },
    "check_switcher": False,
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
}

html_context = {
    "github_user": "ckirua",
    "github_repo": "picop",
    "github_version": "main",
    "doc_path": "doc",
}

suppress_warnings = [
    # Root CHANGELOG.md uses repo-relative Markdown links; keep the include as-is.
    "myst.xref_missing",
]

# -- Stub docstring bridge ----------------------------------------------------
# Public one-liners live in adjacent ``.pyi`` stubs. Compiled Cython modules
# often ship empty ``__doc__``; inject stub docs during autodoc.

_STUB_DOC_CACHE: dict[str, dict[str, str]] = {}


def _stub_path_for_module(modname: str) -> Path | None:
    """Resolve ``picop.foo`` / ``picop.uuid`` to an on-disk ``.pyi`` path."""
    if not modname.startswith("picop"):
        return None
    parts = modname.split(".")
    if len(parts) == 1:
        return None
    rest = parts[1:]
    if rest == ["uuid"] or (len(rest) >= 1 and rest[0] == "uuid"):
        candidate = PACKAGE_SRC / "uuid" / "_uuid.pyi"
        return candidate if candidate.is_file() else None
    if len(rest) == 1:
        candidate = PACKAGE_SRC / f"{rest[0]}.pyi"
        return candidate if candidate.is_file() else None
    # Nested: picop.uuid._uuid already covered; other nests unlikely.
    candidate = PACKAGE_SRC.joinpath(*rest[:-1]) / f"{rest[-1]}.pyi"
    return candidate if candidate.is_file() else None


def _walk_stub_docs(node: ast.AST, prefix: str = "") -> dict[str, str]:
    """Collect docstrings for functions/classes (and nested methods) from a stub AST."""
    out: dict[str, str] = {}
    body = getattr(node, "body", None)
    if body is None:
        return out
    for child in body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            qual = f"{prefix}.{child.name}" if prefix else child.name
            doc = ast.get_docstring(child)
            if doc:
                out[qual] = doc
                out[child.name] = doc  # bare name for member lookup
            if isinstance(child, ast.ClassDef):
                out.update(_walk_stub_docs(child, qual))
        elif isinstance(child, ast.Assign):
            # Rare: documented constants via preceding Expr docstring are not
            # attached by get_docstring; skip for now.
            pass
    return out


def _load_stub_docs(modname: str) -> dict[str, str]:
    if modname in _STUB_DOC_CACHE:
        return _STUB_DOC_CACHE[modname]
    path = _stub_path_for_module(modname)
    docs: dict[str, str] = {}
    if path is not None:
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError:
            # Fall back to a light regex scan so one broken stub cannot abort the build.
            docs = _regex_stub_docs(text)
        else:
            mod_doc = ast.get_docstring(tree)
            if mod_doc:
                docs[""] = mod_doc
            docs.update(_walk_stub_docs(tree))
    _STUB_DOC_CACHE[modname] = docs
    return docs


def _regex_stub_docs(text: str) -> dict[str, str]:
    """Best-effort ``def name`` + following docstring extraction when AST parse fails."""
    import re

    docs: dict[str, str] = {}
    mod = re.match(r'^"""(.*?)"""', text, re.DOTALL)
    if mod:
        docs[""] = mod.group(1).strip()
    for m in re.finditer(
        r"^(?:async\s+)?def\s+(\w+)\s*\([^)]*\)\s*(?:->[^:]+)?:\s*\n"
        r'\s+"""(.*?)"""',
        text,
        re.MULTILINE | re.DOTALL,
    ):
        docs[m.group(1)] = m.group(2).strip()
    return docs


def _stub_doc_for(what: str, name: str, obj: object) -> str | None:
    """Resolve stub docstring for an autodoc object, if any."""
    parts = name.split(".")
    if what == "module" and name.startswith("picop"):
        return _load_stub_docs(name).get("")
    modname = getattr(obj, "__module__", None)
    attr = parts[-1] if parts else name
    if not modname or not str(modname).startswith("picop"):
        # Fully-qualified autodoc name: picop.cydict.dict_get
        if len(parts) >= 3 and parts[0] == "picop":
            modname = ".".join(parts[:-1])
            attr = parts[-1]
        else:
            return None
    stub = _load_stub_docs(str(modname))
    return stub.get(attr) or stub.get(".".join(parts[2:])) if len(parts) > 2 else stub.get(attr)


def _has_prose_docstring(lines: list[str]) -> bool:
    """True if ``lines`` already contain human prose (not only field lists / directives)."""
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(":") or stripped.startswith(".."):
            continue
        return True
    return False


def _process_docstring(app, what, name, obj, options, lines):  # noqa: ARG001
    """If the live object has no prose docstring, inject the adjacent ``.pyi`` one.

    ``sphinx_autodoc_typehints`` may already have inserted ``:param:`` / ``:rtype:``
    fields into ``lines``; treat those as non-prose so stubs still win.
    """
    if _has_prose_docstring(lines):
        return
    doc = _stub_doc_for(what, name, obj)
    if not doc:
        return
    injected = doc.splitlines()
    if lines:
        injected.append("")
        injected.extend(lines)
    lines[:] = injected


def _skip_member(app, what, name, obj, skip, options):  # noqa: ARG001
    """Keep members that lack runtime ``__doc__`` but have stub docstrings."""
    if not skip:
        return False
    modname = getattr(obj, "__module__", None)
    if not modname or not str(modname).startswith("picop"):
        return None
    stub = _load_stub_docs(str(modname))
    if name in stub:
        return False
    return None


def setup(app):
    app.connect("autodoc-process-docstring", _process_docstring)
    app.connect("autodoc-skip-member", _skip_member)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
