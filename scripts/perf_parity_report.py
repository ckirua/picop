#!/usr/bin/env python3
"""Regenerate the perf-parity tables from the Tier A benches.

Runs every ``bench/*_bench.py`` (Tier A, plain-Python baseline) with the
package installed, collects every ``session.compare`` ratio, and prints the
two tables that ``docs/PERF_PARITY.md`` is built from:

* helpers that lose to the builtin in **every** measured case, and
* helpers that win on some inputs and lose on others.

Usage::

    python scripts/perf_parity_report.py                     # tables to stdout
    python scripts/perf_parity_report.py --update-doc        # rewrite docs/PERF_PARITY.md
    python scripts/perf_parity_report.py --sync-stubs        # rewrite the parity notes in the .pyi stubs
    python scripts/perf_parity_report.py --json > /tmp/parity.json   # machine-readable rows
    python scripts/perf_parity_report.py --from-json /tmp/parity.json

Ratios come from the ``BENCH_JSON`` line each bench prints when
``CPY_BENCH_JSON=1`` (set by this script), so no table parsing is involved.

Ratio convention: ``mean(picop) / mean(builtin)`` — above ``1.00`` means the
plain-Python call was faster. A helper counts as a loser only when every case
for it exceeds ``--threshold`` (default 1.02).
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCH_DIR = ROOT / "bench"
PARITY_DOC = ROOT / "docs" / "PERF_PARITY.md"
JSON_MARKER = "BENCH_JSON "


def public_names() -> set[str]:
    return set(public_modules())


def public_modules() -> dict[str, str]:
    """Public barrel helper name -> source module name."""
    tree = ast.parse((ROOT / "src" / "picop" / "__init__.py").read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("cy"):
            for alias in node.names:
                out[alias.name] = node.module
    return out


def _bench_rows(stdout: str) -> list[tuple[str, float, str]]:
    """Pull ``(label, ratio, case)`` from the ``BENCH_JSON`` line a bench prints."""
    for line in stdout.splitlines():
        if line.startswith(JSON_MARKER):
            return [
                (row["label"], float(row["ratio"]), row.get("case") or "default case")
                for row in json.loads(line[len(JSON_MARKER):])
            ]
    return []


def bench_files() -> list[Path]:
    return sorted(
        path
        for path in BENCH_DIR.glob("*.py")
        if path.name != "__init__.py" and not path.name.startswith("_")
    )


def collect() -> tuple[dict[str, list[tuple[float, str]]], list[str]]:
    """Run every bench and return ``label -> [(ratio, case)]`` plus failures."""
    ratios: dict[str, list[tuple[float, str]]] = {}
    failures: list[str] = []
    for path in bench_files():
        env = dict(os.environ)
        env.setdefault("PYTHONPATH", str(ROOT / "src"))
        env["CPY_BENCH_JSON"] = "1"
        try:
            out = subprocess.run(
                [sys.executable, str(path)],
                capture_output=True,
                text=True,
                env=env,
                timeout=900,
            )
        except subprocess.TimeoutExpired:
            failures.append(f"{path.name}: timeout")
            continue
        if out.returncode != 0:
            failures.append(f"{path.name}: exit {out.returncode}")
            continue
        for name, ratio, case in _bench_rows(out.stdout):
            ratios.setdefault(name, []).append((ratio, case))
    return ratios, failures


BUILTIN_LABELS = {
    "int": "int(x)",
    "float": "float(x)",
    "bool": "bool(x)",
    "abs": "abs(x)",
    "len": "len(x)",
    "str": "str(x)",
    "repr": "repr(x)",
    "hash": "hash(x)",
    "type": "type(x)",
    "iter": "iter(x)",
    "callable": "callable(x)",
    "hasattr": "hasattr(x, name)",
    "getattr": "getattr(x, name)",
    "isinstance": "isinstance(x, t)",
    "issubclass": "issubclass(a, b)",
    "pow": "pow(a, b)",
    "divmod": "divmod(a, b)",
    "tuple": "tuple(x)",
    "format": "format(x, spec)",
    "sys.intern": "sys.intern(s)",
    "dir": "dir(x)",
    "gc.isenabled": "gc.isenabled()",
    "weakref.proxy": "weakref.proxy(x)",
    "operator.add": "a + b",
    "operator.sub": "a - b",
    "operator.mul": "a * b",
    "operator.truediv": "a / b",
    "operator.floordiv": "a // b",
    "operator.mod": "a % b",
    "operator.pow": "pow(a, b)",
    "operator.and_": "a & b",
    "operator.or_": "a | b",
    "operator.xor": "a ^ b",
    "operator.invert": "~a",
    "operator.lshift": "a << b",
    "operator.rshift": "a >> b",
    "operator.neg": "-a",
    "operator.pos": "+a",
    "operator.index": "operator.index(x)",
    "operator.getitem": "x[key]",
    "operator.matmul": "a @ b",
    "operator.iadd": "a += b",
    "operator.isub": "a -= b",
    "operator.imul": "a *= b",
    "operator.itruediv": "a /= b",
    "operator.ifloordiv": "a //= b",
    "operator.imod": "a %= b",
    "operator.iand": "a &= b",
    "operator.ior": "a |= b",
    "operator.ixor": "a ^= b",
    "operator.ilshift": "a <<= b",
    "operator.irshift": "a >>= b",
    "codecs.strict_errors": "codecs.strict_errors",
    "codecs.replace_errors": "codecs.replace_errors",
    "codecs.ignore_errors": "codecs.ignore_errors",
    "codecs.backslashreplace_errors": "codecs.backslashreplace_errors",
    "codecs.namereplace_errors": "codecs.namereplace_errors",
    "codecs.lookup": "codecs.lookup(enc).decode(b, err)",
    "str.endswith": "s.endswith(suffix)",
    "str.startswith": "s.startswith(prefix)",
    "str.encode": "s.encode('utf-8')",
    "datetime.time": "datetime.time(...)",
    "__import__": "__import__(name)",
}
LAMBDA_LABELS = {
    "lambda o: o.fileno()": "x.fileno()",
    "lambda m: m.__file__": "module.__file__",
    "lambda m, k, v: setattr(m, k.decode(), v) or 0": "setattr(m, name, v)",
    "lambda o, a, b: o[a:b]": "x[a:b]",
    "lambda o: o.year": "dt.year",
    "lambda o: o.month": "dt.month",
    "base_dupdate": "d.update(it)",
    "base_ddel": "del d[key]",
    "base_dpop": "d.pop(key)",
    "base_dclear": "d.clear()",
    "base_dcopy": "d.copy()",
    "base_dmerge": "d1 | d2",
    "base_dmerge_seq": "d.update(pairs)",
    "base_dset": "d[key] = value",
    "base_dsetdefault": "d.setdefault(key, default)",
    "base_dsetdefault_ref": "d.setdefault(key, default)",
    "b_lappend": "lst.append(x)",
    "b_lset_item": "lst[i] = value",
    "b_lset_slice": "lst[a:b] = values",
    "b_lclear": "lst.clear()",
    "b_lcopy": "lst.copy()",
    "b_lextend": "lst.extend(it)",
    "b_linsert": "lst.insert(i, x)",
    "b_lreverse": "lst.reverse()",
    "b_lsort": "lst.sort()",
    "py_lget": "lst[i]",
    "py_lslice": "lst[a:b]",
    "py_las_tuple": "tuple(lst)",
    "py_tget": "t[i]",
    "py_tlen": "len(t)",
    "py_tpack2": "(a, b)",
    "py_tpack3": "(a, b, c)",
    "py_tslice": "t[a:b]",
    "py_scopy": "s.copy()",
    "py_snew": "set(it)",
    "py_sfrozen_new": "frozenset(it)",
    "py_dcontains": "key in d",
    "py_ne": "a != b",
    "py_beq": "a == b",
    "py_blen": "len(b)",
    "py_cmp": "a == b",
    "py_sentinel_new": "sentinel(name)",
    "py_sentinel_type": "the sentinel singleton",
    "py_depth": "walk ``tb_next``",
    "b_dis_en": "gc.disable(); gc.enable()",
    "b_sadd": "s.add(v)",
    "b_spop": "s.pop()",
    "b_sdiscard_hit": "s.discard(v)",
    "b_sdiscard_miss": "s.discard(v)",
    "b_sclear": "s.clear()",
    "b_supdate": "s.update(it)",
    "_wrap_err(codecs.strict_errors)": "codecs.lookup(enc).decode(b, 'strict')",
    "_py_ctxvar_reset": "var.reset(token)",
    "_inc_dec": "codecs.incremental_decoder(enc)",
    "py_eq": "==",
    "py_frozendict_new": "frozendict(obj)",
    "fn_get": "f.__defaults__",
}
REASON_BY_MODULE = {
    "cybool": "returns the C ``bool`` for a Cython ``int``",
    "cycodecs": "codec/error-handler bridge for extension authors",
    "cydatetime": "builds C datetime objects without the class machinery",
    "cydict": "unchecked ``PyDict`` mutation on a known dict",
    "cyfloat": "hands Cython a C ``double``",
    "cylong": "hands Cython a C integer type",
    "cymodule": "module plumbing for embedding code",
    "cynumber": "protocol bridge for unknown number types",
    "cyobject": "last-resort bridge for unknown objects",
    "cysequence": "works on any sequence, not just ``list``",
    "cyset": "unchecked set mutation",
    "cystr": "``PyUnicode_GET_LENGTH`` on a known compact ``str``",
    "cyunicode": "interning on the typed Cython path",
    "cyfunction": "function defaults without the Python attribute machinery",
    "cyweakref": "weak-reference creation from C",
    "cycontextvars": "context-variable token plumbing",
    "cygc": "GC state getter",
    "cycomplex": "unpacks a ``complex`` into C doubles",
    "cybuffer": "buffer-protocol comparison",
    "cybytes": "byte-string bridge for unknown bytes-like objects",
    "cytuple": "tuple bridge for unknown sequences",
    "cyrange": "range-protocol bridge",
    "cylist": "unchecked ``PyList`` mutation on a known list",
    "cysentinel": "sentinel-singleton bridge for extension authors",
    "cyfrozendict": "the 3.15 ``frozendict`` bridge",
    "cyiterator": "iterator-protocol bridge",
    "cymemoryview": "memoryview attribute bridge",
}


def _builtin_for(label: str, baselines: dict[str, set[str]]) -> str:
    options = sorted(baselines.get(label, []))
    for option in options:
        if option in BUILTIN_LABELS or option in LAMBDA_LABELS:
            return BUILTIN_LABELS.get(option, LAMBDA_LABELS.get(option, option))
    return options[0] if options else "-"


def _mean(cases: list[tuple[float, str]]) -> float:
    return sum(ratio for ratio, _ in cases) / len(cases)


def module_of(name: str) -> str:
    for stub in sorted((ROOT / "src" / "picop").rglob("*.pyi")):
        try:
            tree = ast.parse(stub.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
                return stub.stem
    return "cy" + name.split("_")[0]


def collect_baselines() -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for path in bench_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("compare", "compare_mutate")
                and len(node.args) >= 3
                and isinstance(node.args[0], ast.Constant)
            ):
                out.setdefault(node.args[0].value, set()).add(ast.unparse(node.args[2]))
    return out


def classify(ratios: dict[str, list[tuple[float, str]]], pub: set[str], threshold: float):
    always: list[tuple[str, list[tuple[float, str]]]] = []
    mixed: list[tuple[str, list[tuple[float, str]]]] = []
    for name, cases in sorted(ratios.items()):
        if name not in pub:
            continue
        values = [ratio for ratio, _ in cases]
        lo, hi = min(values), max(values)
        if lo > threshold:
            always.append((name, cases))
        elif hi > threshold:
            mixed.append((name, cases))
    return always, mixed


PARITY_NOTE = "Slower than the plain-Python equivalent"
MIXED_NOTE = "Mixed Tier A parity"
ALWAYS_HEADER = "## Always slower from pure Python"
MIXED_HEADER = "## Slower only on some inputs"


def hot_names() -> set[str]:
    """Names exported by ``picop.hot`` (the frozen Core surface)."""
    tree = ast.parse((ROOT / "src" / "picop" / "hot.py").read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    names.update(
                        element.id
                        for element in getattr(node.value, "elts", [])
                        if isinstance(element, ast.Constant)
                    )
    return names


def run_config() -> str:
    import platform
    import sysconfig

    gil = "GIL off" if sysconfig.get_config_var("Py_GIL_DISABLED") else "GIL on"
    n = os.environ.get("CPY_BENCH_N", "80_000").replace("_", "")
    runs = os.environ.get("CPY_BENCH_RUNS", "5")
    return (
        f"CPython {sys.version.split()[0]} · {platform.system()} {platform.machine()} "
        f"· {gil} · `N={n} RUNS={runs}`"
    )


def _band(cases: list[tuple[float, str]]) -> str:
    lo, hi = min(r for r, _ in cases), max(r for r, _ in cases)
    return f"{lo:.2f}x" if lo == hi else f"{lo:.2f}–{hi:.2f}x"


def stats_paragraph(ratios, pub, baselines, threshold: float, config: str | None = None) -> str:
    names = [name for name in ratios if name in pub]
    cases = [ratio for name in names for ratio, _ in ratios[name]]
    always = [name for name in names if min(r for r, _ in ratios[name]) > threshold]
    mixed = [name for name in names if not (min(r for r, _ in ratios[name]) > threshold)
             and max(r for r, _ in ratios[name]) > threshold]
    above = sum(1 for ratio in cases if ratio > threshold)
    hot = sorted(hot_names() & set(always))
    if hot:
        if len(hot) == 1:
            core_note = f"the only Core / `picop.hot` helper among them is `{hot[0]}`"
        else:
            listed = ", ".join(f"`{name}`" for name in hot[:-1]) + f" and `{hot[-1]}`"
            core_note = f"the Core / `picop.hot` helpers among them are {listed}"
    else:
        core_note = "none of them are Core / `picop.hot` helpers"
    return (
        f"Current run ({config or run_config()}): **{len(cases)}** Tier A cases across "
        f"**{len({pub[name] for name in names})}** public modules, **mean "
        f"{sum(cases) / len(cases):.2f}x**. {above} cases "
        f"({100 * above / len(cases):.0f}%) land above `{threshold}x`, and {core_note} — "
        "every other loss is a Protocols or Runtime thin wrapper."
    )


def always_rows(ratios, pub, baselines, modules, threshold: float) -> str:
    rows = ["| Helper | Module | Ratio | Use instead | Why |", "|---|---|---|---|---|"]
    for name, cases in sorted(
        classify(ratios, pub, threshold)[0], key=lambda item: (-_mean(item[1]), item[0])
    ):
        rows.append(
            f"| `{name}` | `{modules.get(name, module_of(name))}` | "
            f"{_mean(cases):.2f}x | `{_builtin_for(name, baselines)}` | "
            f"{REASON_BY_MODULE.get(modules.get(name, ''), 'thin C-API wrapper')} |"
        )
    count = len(rows) - 2
    return "\n".join(rows) + (
        f"\n\n*({count} helpers. Ratios are the mean across each helper's Tier A cases; "
        "regenerate with `python scripts/perf_parity_report.py --update-doc`.)*"
    )


def mixed_rows(ratios, pub, threshold: float) -> str:
    rows = ["| Helper | Best case | Worst case |", "|---|---|---|"]
    for name, cases in sorted(
        classify(ratios, pub, threshold)[1], key=lambda item: (_mean(item[1]), item[0])
    ):
        best = min(cases, key=lambda item: item[0])
        worst = max(cases, key=lambda item: item[0])
        rows.append(
            f"| `{name}` | {best[0]:.2f}x (`{best[1] or 'default input'}`) | "
            f"{worst[0]:.2f}x (`{worst[1] or 'default input'}`) |"
        )
    return "\n".join(rows)


def _replace_section(text: str, header: str, body: str) -> str:
    start = text.index(header) + len(header)
    end = text.index("\n## ", start) if "\n## " in text[start:] else len(text)
    return text[:start] + "\n\n" + body.rstrip() + "\n" + text[end:]


def update_doc(ratios, pub, baselines, threshold: float, config: str | None = None) -> str:
    text = PARITY_DOC.read_text(encoding="utf-8")
    modules = {name: pub[name] for name in ratios if name in pub}
    start = text.index("Current run (")
    end = text.index("\n\n", start)
    text = text[:start] + stats_paragraph(ratios, pub, baselines, threshold, config) + text[end:]
    text = _replace_section(text, ALWAYS_HEADER, always_rows(ratios, pub, baselines, modules, threshold))
    text = _replace_section(
        text,
        MIXED_HEADER,
        "These win on most cases and lose on a narrow band. Keep them; know the crossover.\n\n"
        + mixed_rows(ratios, pub, threshold),
    )
    PARITY_DOC.write_text(text, encoding="utf-8")
    return text


def sync_stub_notes(ratios, pub, baselines, threshold: float) -> int:
    """Rewrite the parity note in every public ``.pyi`` docstring from ``ratios``.

    Helpers that lose every Tier A case get ``Slower than the plain-Python equivalent
    …``; helpers that win on some inputs get ``Mixed Tier A parity: …``. Helpers that
    win everywhere keep no note. Idempotent: running it twice changes nothing.
    """
    always = {name: cases for name, cases in classify(ratios, pub, threshold)[0]}
    mixed = {name: cases for name, cases in classify(ratios, pub, threshold)[1]}
    modules = {name: pub[name] for name in pub}
    updated = 0
    for stub in sorted((ROOT / "src" / "picop").rglob("*.pyi")):
        source = stub.read_text(encoding="utf-8")
        lines = source.splitlines()
        edits: list[tuple[int, int, str]] = []
        for node in ast.parse(source).body:
            if not isinstance(node, ast.FunctionDef) or node.name.startswith("_"):
                continue
            doc_node = node.body[0]
            if not (
                isinstance(doc_node, ast.Expr)
                and isinstance(doc_node.value, ast.Constant)
                and isinstance(doc_node.value.value, str)
            ):
                continue
            name = node.name
            reason = REASON_BY_MODULE.get(modules.get(name, ""), "the typed Cython call site")
            if name in always:
                target = (
                    f"{PARITY_NOTE} ``{_builtin_for(name, baselines)}`` "
                    f"(Tier A {_band(always[name])}); {reason}."
                )
            elif name in mixed:
                cases = ", ".join(
                    f"{ratio:.2f}x ({case or 'default input'})"
                    for ratio, case in sorted(mixed[name])
                )
                target = f"{MIXED_NOTE}: {cases}; {reason}."
            else:
                target = ""
            indent = " " * (node.col_offset + 4)
            new_doc = _rewrite_doc(doc_node.value.value, target, indent)
            if new_doc == _dedent(doc_node.value.value, indent).rstrip("\n"):
                continue
            if "\n" in new_doc:
                replacement = [indent + '"""' + new_doc.splitlines()[0]] + [
                    indent + line if line else "" for line in new_doc.splitlines()[1:]
                ] + [indent + '"""']
            else:
                replacement = [indent + f'"""{new_doc}"""']
            edits.append((doc_node.lineno, doc_node.end_lineno, "\n".join(replacement)))
        if not edits:
            continue
        for start, end, replacement in reversed(edits):
            lines[start - 1:end] = replacement.splitlines()
            updated += 1
        stub.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return updated


def _dedent(doc: str, indent: str) -> str:
    return "\n".join(
        line[len(indent):] if line.startswith(indent) else line for line in doc.splitlines()
    )


def _rewrite_doc(doc: str, target: str, indent: str) -> str:
    """Return ``doc`` with the parity note as the first Notes paragraph."""
    lines = _dedent(doc, indent).splitlines()
    notes_at = next(
        (
            index
            for index, line in enumerate(lines)
            if line.strip() == "Notes"
            and index + 1 < len(lines)
            and lines[index + 1].strip() == "-----"
        ),
        None,
    )
    if notes_at is None:
        for index, line in enumerate(lines):
            if line.strip().startswith("Notes:"):
                rest = line.strip()[len("Notes:") :].strip()
                if rest:
                    rest = rest[0].upper() + rest[1:]
                lines[index : index + 1] = ["Notes", "-----", *([rest] if rest else [])]
                notes_at = index
                break
    head = (
        "\n".join(lines[:notes_at]).rstrip()
        if notes_at is not None
        else "\n".join(lines).rstrip()
    )
    paragraphs: list[list[str]] = []
    if notes_at is not None:
        current: list[str] = []
        for line in lines[notes_at + 2:]:
            if not line.strip():
                if current:
                    paragraphs.append(current)
                    current = []
                continue
            current.append(line.rstrip())
        if current:
            paragraphs.append(current)
    kept = [
        paragraph
        for paragraph in paragraphs
        if not paragraph[0].strip().startswith((PARITY_NOTE, MIXED_NOTE))
    ]
    if target:
        kept.insert(0, textwrap.wrap(target, width=84 - len(indent)))
    if not kept:
        return head
    return head + "\n\nNotes\n-----\n" + "\n\n".join("\n".join(paragraph) for paragraph in kept)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--threshold", type=float, default=1.02)
    ap.add_argument("--json", action="store_true", help="emit raw label/ratio rows")
    ap.add_argument(
        "--update-doc",
        action="store_true",
        help="rewrite the stats line and both tables in docs/PERF_PARITY.md",
    )
    ap.add_argument(
        "--sync-stubs",
        action="store_true",
        help="rewrite the parity notes in the .pyi stubs to match the tables",
    )
    ap.add_argument(
        "--from-json",
        type=Path,
        help="reuse a previous --json dump instead of re-running the benches",
    )
    args = ap.parse_args()

    pub = public_modules()
    config = None
    if args.from_json:
        data = json.loads(args.from_json.read_text(encoding="utf-8"))
        ratios, failures = data["ratios"], data["failures"]
        config = data.get("config")
    else:
        ratios, failures = collect()
        config = run_config()
    if failures:
        print("bench failures:", file=sys.stderr)
        for line in failures:
            print("  " + line, file=sys.stderr)

    baselines = collect_baselines()
    modules = {name: pub[name] for name in ratios if name in pub}

    if args.update_doc:
        update_doc(ratios, pub, baselines, args.threshold, config)
        print(f"rewrote {PARITY_DOC.relative_to(ROOT)}")
    if args.sync_stubs:
        print(f"synced {sync_stub_notes(ratios, pub, baselines, args.threshold)} docstring notes")
    if args.json:
        json.dump({"ratios": ratios, "failures": failures, "config": config}, sys.stdout, indent=2)
    if not args.update_doc and not args.sync_stubs and not args.json:
        print(always_rows(ratios, pub, baselines, modules, args.threshold))
        print()
        print(mixed_rows(ratios, pub, args.threshold))

    always, mixed = classify(ratios, pub, args.threshold)
    cases = sum(len(row) for name, row in ratios.items() if name in pub)
    print(
        f"{len(always)} helpers always slower, {len(mixed)} mixed, "
        f"{cases} Tier A cases measured",
        file=sys.stderr,
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
