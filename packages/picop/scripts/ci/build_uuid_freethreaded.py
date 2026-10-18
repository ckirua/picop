"""Build only the UUID extension for CPython free-threaded compatibility CI."""

from __future__ import annotations

from pathlib import Path
import sysconfig

from Cython.Build import cythonize
from setuptools import Distribution, Extension
from setuptools.command.build_ext import build_ext


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = PROJECT_ROOT / "src"
UUID_SOURCE_ROOT = SOURCE_ROOT / "picop" / "uuid"
BUILD_ROOT = PROJECT_ROOT / "build" / "uuid-freethreaded" / sysconfig.get_config_var("SOABI")


def main() -> None:
    native_extension = Extension(
        "picop.uuid._uuid_native",
        sources=[str(UUID_SOURCE_ROOT / "_uuid_native.c")],
        include_dirs=[str(UUID_SOURCE_ROOT)],
        extra_compile_args=["-std=c11", "-O3", "-Wno-unused-function"],
        language="c",
    )
    extension = Extension(
        "picop.uuid._uuid",
        sources=[
            str(UUID_SOURCE_ROOT / "_uuid.pyx"),
            str(UUID_SOURCE_ROOT / "uuid.c"),
        ],
        include_dirs=[str(UUID_SOURCE_ROOT)],
        libraries=["crypto"],
        extra_compile_args=[
            "-std=c11", "-O3", "-Wno-unused-function", "-Wno-unused-variable",
        ],
        language="c",
    )

    # The private native type must exist before the Cython module attaches methods.
    extensions = cythonize(
        [native_extension, extension],
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
