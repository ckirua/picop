#!/usr/bin/env python3
"""Syntax-check every shim header with a strict C11 compiler.

gcc/clang accept GNU extensions that MSVC rejects — arithmetic on `void *` is the
classic example (MSVC: ``error C2036: 'void *': unknown size``). Shims are
header-only, so a helper that builds on Linux can still break the Windows wheels.
This compiles each ``src/picop/*_shim.h`` with ``-std=c11 -pedantic-errors -Werror``
against the running interpreter's headers and fails on any diagnostic.

    python scripts/check_shims_pedantic.py

Requires a C compiler on PATH; skips (with a warning) when none is found or when
the interpreter ships no headers.
"""

from __future__ import annotations

import subprocess
import sys
import sysconfig
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHIMS = sorted((ROOT / "src" / "picop").glob("*_shim.h"))


def compiler() -> list[str] | None:
    for candidate in ("gcc", "clang"):
        probe = subprocess.run([candidate, "--version"], capture_output=True, text=True)
        if probe.returncode == 0:
            return [candidate]
    return None


def main() -> int:
    cc = compiler()
    if cc is None:
        print("warning: no C compiler on PATH; skipping shim pedantic check")
        return 0

    includes = sysconfig.get_paths()["include"]
    if not Path(includes).joinpath("Python.h").exists():
        print(f"warning: no Python headers in {includes}; skipping shim pedantic check")
        return 0

    failures: list[str] = []
    for header in SHIMS:
        result = subprocess.run(
            [
                *cc,
                "-std=c11",
                "-pedantic-errors",
                "-Werror",
                "-fsyntax-only",
                f"-I{includes}",
                f"-I{ROOT / 'src' / 'picop'}",
                "-include",
                "Python.h",
                str(header),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            failures.append(f"{header.relative_to(ROOT)}\n{result.stdout.strip()}\n{result.stderr.strip()}")

    if failures:
        print(f"{len(failures)} shim header(s) fail a strict C11 compile:", file=sys.stderr)
        for block in failures:
            print("  " + block.replace("\n", "\n  "), file=sys.stderr)
        return 1
    print(f"check_shims_pedantic OK: {len(SHIMS)} shim headers compile with -std=c11 -pedantic-errors -Werror")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
