"""Build the out-of-tree ``demo`` extension in-place against an installed picop.

Run from this directory after ``pip install -e .`` (or a wheel) at the repo root::

    python setup.py build_ext --inplace
"""

from __future__ import annotations

from Cython.Build import cythonize
from setuptools import Extension, setup

setup(
    name="picop_cimport_ext_demo",
    ext_modules=cythonize(
        [
            Extension(
                "demo",
                ["demo.pyx"],
                language="c",
                extra_compile_args=[
                    "-O3",
                    "-Wno-unused-function",
                    "-Wno-unused-variable",
                ],
            )
        ],
        compiler_directives={"language_level": "3"},
    ),
)
