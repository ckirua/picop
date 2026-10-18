"""Compile Tier B ``*_tb.pyx`` extensions in-place under ``bench/tier_b/``.

Usage (repo root)::

    python -m bench.tier_b.build
    python -m bench.tier_b.build cytuple cybytes
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT / "src"


def _modules(requested: list[str] | None) -> list[str]:
    found = sorted(p.stem.removesuffix("_tb") for p in HERE.glob("*_tb.pyx"))
    if not requested:
        return found
    missing = [name for name in requested if name not in found]
    if missing:
        msg = f"no *_tb.pyx for: {', '.join(missing)} (have: {', '.join(found) or 'none'})"
        raise SystemExit(msg)
    return requested


def build(modules: list[str] | None = None) -> list[str]:
    from Cython.Build import cythonize
    from setuptools import Extension
    from setuptools.command.build_ext import build_ext as _build_ext
    from setuptools.dist import Distribution

    names = _modules(modules)
    if not names:
        print("no *_tb.pyx files to build", file=sys.stderr)
        raise SystemExit(1)

    # Prefer already-built .so when sources are older (fast re-run).
    todo: list[str] = []
    for name in names:
        pyx = HERE / f"{name}_tb.pyx"
        sos = list(HERE.glob(f"{name}_tb*.so")) + list(HERE.glob(f"{name}_tb*.pyd"))
        if sos and all(so.stat().st_mtime >= pyx.stat().st_mtime for so in sos):
            print(f"up-to-date: {name}_tb")
            continue
        todo.append(name)

    if not todo:
        return names

    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    ext_modules = cythonize(
        [
            Extension(
                name=f"{name}_tb",
                sources=[str(HERE / f"{name}_tb.pyx")],
                include_dirs=[str(SRC), str(SRC / "cypy")],
                extra_compile_args=[
                    "-O3",
                    "-march=native",
                    "-Wno-unused-function",
                    "-Wno-unused-variable",
                ],
                language="c",
            )
            for name in todo
        ],
        compiler_directives={
            "language_level": "3",
            "boundscheck": False,
            "wraparound": False,
            "initializedcheck": False,
        },
        annotate=False,
    )

    class _InplaceBuild(_build_ext):
        def finalize_options(self) -> None:  # noqa: ANN001
            super().finalize_options()
            self.inplace = True
            self.build_lib = str(HERE)
            self.build_temp = str(HERE / "_build_temp")

    dist = Distribution({"name": "cypy_tier_b", "ext_modules": ext_modules})
    dist.package_dir = {"": str(HERE)}
    cmd = _InplaceBuild(dist)
    cmd.ensure_finalized()
    cmd.run()
    print(f"built: {', '.join(todo)}")
    return names


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "modules",
        nargs="*",
        help="module stems (e.g. cytuple); default = all *_tb.pyx",
    )
    args = ap.parse_args()
    os.chdir(HERE)
    build(args.modules or None)


if __name__ == "__main__":
    main()
