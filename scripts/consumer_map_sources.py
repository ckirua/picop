"""Source-derived consumer surface for the complete replacement catalog."""
from __future__ import annotations

import ast
import re
from pathlib import Path

from ops_inventory_coverage import public_barrel


def _cimports(path: Path):
    """Yield source-located imports, parsing only each collected Cython statement."""
    lines = path.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if not re.match(r"^\s*from\b.*\bcimport\b", line):
            continue
        start = index
        statement = line.strip()
        depth = statement.split("#", 1)[0].count("(") - statement.split("#", 1)[0].count(")")
        while depth > 0 and index < len(lines):
            part = lines[index]
            index += 1
            statement += "\n" + part
            code = part.split("#", 1)[0]
            depth += code.count("(") - code.count(")")
        if depth != 0:
            raise ValueError(f"{path}:{start}: unbalanced cimport")
        try:
            parsed = ast.parse(re.sub(r"\bcimport\b", "import", statement, count=1))
        except SyntaxError as exc:
            raise ValueError(f"{path}:{start}: unsupported cimport: {exc.msg}") from exc
        if len(parsed.body) != 1 or not isinstance(parsed.body[0], ast.ImportFrom):
            raise ValueError(f"{path}:{start}: unsupported cimport statement")
        node = parsed.body[0]
        module = "." * node.level + (node.module or "")
        for alias in node.names:
            if alias.name == "*":
                raise ValueError(f"{path}:{start}: wildcard cimport is unsupported")
            yield module, alias.name, alias.asname or alias.name, start


def _python_exports(path: Path) -> list[tuple[str, str]]:
    names = iter(public_barrel(path))
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    out = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("cy"):
            for alias in node.names:
                if alias.name == "*":
                    raise ValueError(f"{path}:{node.lineno}: wildcard import is unsupported")
                try:
                    out.append((node.module, next(names)))
                except StopIteration as exc:
                    raise ValueError(f"{path}:{node.lineno}: inconsistent public_barrel output") from exc
    try:
        next(names)
    except StopIteration:
        return out
    raise ValueError(f"{path}: inconsistent public_barrel output")


def _kind(root: Path, module: str, name: str) -> str:
    base = root / "src" / "picop" / Path(*module.split("."))
    pyi = base.with_suffix(".pyi")
    if pyi.exists():
        tree = ast.parse(pyi.read_text(encoding="utf-8"), filename=str(pyi))
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
                return "function"
            if isinstance(node, ast.ClassDef) and node.name == name:
                return "class"
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                if any(isinstance(t, ast.Name) and t.id == name for t in targets):
                    return "constant"

    pxd = base.with_suffix(".pxd")
    if pxd.exists():
        lines = pxd.read_text(encoding="utf-8").splitlines()
        enum_indent: int | None = None
        for line in lines:
            stripped = line.strip()
            indent = len(line) - len(line.lstrip())
            if enum_indent is not None and stripped and indent <= enum_indent:
                enum_indent = None
            if re.match(rf"ctypedef\s+enum\s+{re.escape(name)}\s*:", stripped):
                return "type"
            if re.match(rf"cdef\s+class\s+{re.escape(name)}\s*:", stripped):
                return "class"
            if re.match(r"ctypedef\s+enum(?:\s+\w+)?\s*:", stripped):
                enum_indent = indent
                continue
            if enum_indent is not None and indent > enum_indent and stripped == name:
                return "constant"
            if re.search(rf"\bctypedef\b.*\b{re.escape(name)}\b", stripped):
                return "type"
            if stripped.startswith(("#", "from ", "cimport ", "cdef extern")):
                continue
            if re.search(rf"\b(?:cp?def|def)\b.*\b{re.escape(name)}\s*\(", stripped):
                return "function"
            # C declarations may spell an exported name before a quoted linker
            # alias, as in `void cs_begin \"picop_cs_begin\" (...)`.
            if re.match(rf"(?:cdef\s+)?(?:inline\s+)?[\w* ]+\b{re.escape(name)}(?:\s+\"[^\"]+\")?\s*\(", stripped):
                return "function"
            if re.match(rf"(?:cdef\s+)?(?:const\s+)?[\w* ]+\b{re.escape(name)}\s*(?:=|$)", stripped):
                return "constant"
        for imported_module, imported_name, _alias, _line in _cimports(pxd):
            if imported_name != name:
                continue
            if imported_module.startswith("."):
                provider = imported_module.lstrip(".")
                if provider.startswith("cy"):
                    return _kind(root, provider, name)
            # External declarations retained through a picop re-export are
            # typed values except for conventionally named constants.
            return "constant" if name.isupper() else "type"
    raise ValueError(f"cannot resolve declaration {module}.{name}")


def enumerate_sources(root: Path) -> dict[str, dict[str, str]]:
    """Map canonical ``picop.<module>.<symbol>`` keys to kind/access."""
    root = Path(root).resolve()
    package = root / "src" / "picop"
    result: dict[str, dict[str, str]] = {}

    def add(module: str, name: str, access: str, kind: str | None = None):
        key = f"picop.{module}.{name}"
        kind = kind or _kind(root, module, name)
        old = result.get(key)
        if old:
            if old["kind"] != kind:
                raise ValueError(f"conflicting source kinds for {key}")
            if old["access"] != access:
                old["access"] = "both"
        else:
            result[key] = {"kind": kind, "access": access}

    for module, name in _python_exports(package / "__init__.py"):
        add(module, name, "python")

    # Root pxd imports identify the actual provider module. This also resolves
    # ``from picop cimport ...`` in examples without inventing picop-level keys.
    root_provider: dict[str, str] = {}
    for mod, name, _alias, _line in _cimports(package / "__init__.pxd"):
        mod = mod.lstrip(".")
        if mod == "uuid":
            mod = "uuid._uuid"
        if not mod.startswith("cy") and mod != "uuid._uuid":
            raise ValueError(f"{package / '__init__.pxd'}: unresolved provider module {mod!r}")
        root_provider[name] = mod
        add(mod, name, "cimport")

    examples = root / "examples"
    if examples.exists():
        for path in sorted(examples.rglob("*.pyx")):
            for mod, name, _alias, line in _cimports(path):
                if mod == "picop":
                    if name not in root_provider:
                        raise ValueError(f"{path}:{line}: unresolved package cimport {name}")
                    mod = root_provider[name]
                elif mod.startswith("picop."):
                    mod = mod[len("picop."):]
                else:
                    # cpython/libc imports are dependencies, not picop APIs.
                    continue
                if mod.startswith("uuid.") and mod == "uuid._uuid":
                    pass
                elif not mod.startswith("cy"):
                    raise ValueError(f"{path}:{line}: unsupported picop cimport module {mod!r}")
                add(mod, name, "cimport")

    # UUID's explicit package re-exports are outside the cy* Python barrel.
    uuid_init = package / "uuid" / "__init__.py"
    tree = ast.parse(uuid_init.read_text(encoding="utf-8"), filename=str(uuid_init))
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "_uuid":
            for alias in node.names:
                add("uuid._uuid", alias.name, "python")

    # Public stub class members, including declared dunders (but not inherited).
    for key, info in list(result.items()):
        if info["kind"] != "class":
            continue
        module, cls = key[len("picop."):].rsplit(".", 1)
        stub = package / f"{module}.pyi"
        if not stub.exists():
            continue
        tree = ast.parse(stub.read_text(encoding="utf-8"), filename=str(stub))
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == cls:
                for member in node.body:
                    if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        kind = "property" if any(isinstance(d, ast.Name) and d.id == "property" for d in member.decorator_list) else "method"
                        add(module, f"{cls}.{member.name}", info["access"], kind)
                    elif isinstance(member, ast.AnnAssign) and isinstance(member.target, ast.Name):
                        add(module, f"{cls}.{member.target.id}", info["access"], "property")

    # UUID is declared in its dedicated private stub, not a cy*-module stub.
    uuid_stub = package / "uuid" / "_uuid.pyi"
    tree = ast.parse(uuid_stub.read_text(encoding="utf-8"), filename=str(uuid_stub))
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "UUID":
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    kind = "property" if any(isinstance(d, ast.Name) and d.id == "property" for d in member.decorator_list) else "method"
                    add("uuid._uuid", f"UUID.{member.name}", "python", kind)
                elif isinstance(member, ast.AnnAssign) and isinstance(member.target, ast.Name):
                    add("uuid._uuid", f"UUID.{member.target.id}", "python", "property")

    # Writer methods exposed by the Cython class declaration are part of its API.
    for module, cls in (("cybytes", "BytesWriter"), ("cyunicode", "UnicodeWriter")):
        class_key = f"picop.{module}.{cls}"
        path = package / f"{module}.pxd"
        if class_key not in result or not path.exists():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        active = False
        base_indent = 0
        for line in lines:
            if re.match(rf"\s*cdef class {cls}\s*:", line):
                active = True
                base_indent = len(line) - len(line.lstrip())
                continue
            indent = len(line) - len(line.lstrip())
            stripped = line.strip()
            if active and stripped and indent <= base_indent:
                active = False
            if active and stripped:
                match = re.search(r"\b([A-Za-z_]\w*)\s*\(", stripped)
                if match and not match.group(1).startswith("_"):
                    add(module, f"{cls}.{match.group(1)}", "cimport", "method")
    return result


def source_counts(root: Path, sources: dict[str, dict[str, str]] | None = None) -> dict[str, int]:
    """Return separate, potentially overlapping surface categories."""
    sources = sources if sources is not None else enumerate_sources(root)
    python_barrel = len(_python_exports(Path(root) / "src" / "picop" / "__init__.py"))
    return {
        "python_barrel": python_barrel,
        "supplemental": sum(1 for row in sources.values() if row["access"] == "cimport" and row["kind"] == "function"),
        "uuid": sum(1 for key in sources if key.startswith("picop.uuid._uuid.")),
        "class_members": sum(1 for row in sources.values() if row["kind"] in ("method", "property")),
        "companions": sum(1 for row in sources.values() if row["kind"] in ("type", "constant", "class")),
    }
