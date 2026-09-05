"""Build only the UUID extension for CPython free-threaded compatibility CI."""

from __future__ import annotations

from pathlib import Path

from Cython.Build import cythonize
from setuptools import Distribution, Extension
from setuptools.command.build_ext import build_ext


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = PROJECT_ROOT / "src"
UUID_SOURCE_ROOT = SOURCE_ROOT / "picop" / "uuid"
BUILD_ROOT = PROJECT_ROOT / "build" / "uuid-freethreaded"


def main() -> None:
    extension = Extension(
        "picop.uuid._uuid",
        sources=[
            str(UUID_SOURCE_ROOT / "_uuid.pyx"),
            str(UUID_SOURCE_ROOT / "uuid.c"),
        ],
        include_dirs=[str(UUID_SOURCE_ROOT)],
        libraries=["crypto"],
        extra_compile_args=[
            "-std=c11",
            "-O3",
            "-march=native",
            "-Wno-unused-function",
            "-Wno-unused-variable",
        ],
        language="c",
    )

    # This extension requires the GIL. Do not mark it free-threading compatible:
    # CPython 3.14t must enable its GIL compatibility mode when loading it.
    extensions = cythonize(
        [extension],
        build_dir=str(BUILD_ROOT / "cython"),
        compiler_directives={"language_level": 3},
    )

    distribution = Distribution(
        {
            "name": "cypy-uuid-freethreaded-build",
            "ext_modules": extensions,
        }
    )
    command = build_ext(distribution)
    command.ensure_finalized()
    command.build_lib = str(SOURCE_ROOT)
    command.build_temp = str(BUILD_ROOT / "temp")
    command.inplace = False
    command.run()


if __name__ == "__main__":
    main()
