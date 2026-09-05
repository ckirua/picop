import os

from picobuild import Extension, cythonize, find_packages, setup

# Portable by default for redistributable wheels/sdists.
# Set CPY_NATIVE=1 for local benches that want -march=native.
_compile_args = [
    "-O3",
    "-Wno-unused-function",
    "-Wno-unused-variable",
]
if os.environ.get("CPY_NATIVE", "").strip() in ("1", "true", "yes"):
    _compile_args.insert(1, "-march=native")

# Cython extensions — same shape as cycel.core.cpy, package name ``picop`` (``cypy`` soft shim).
cythonized_extensions = cythonize(
    [
        Extension(
            "picop.uuid._uuid",
            [
                "src/picop/uuid/_uuid.pyx",
                "src/picop/uuid/uuid.c",
            ],
            include_dirs=["src/picop/uuid"],
            extra_compile_args=_compile_args,
            libraries=["crypto"],
            language="c",
        ),
        Extension(
            "picop.*",
            ["src/picop/*.pyx"],
            include_dirs=["src/picop"],
            extra_compile_args=_compile_args,
            language="c",
        ),
    ]
)


if __name__ == "__main__":
    setup(
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        package_data={
            "picop": ["py.typed", "**/*.pxd", "**/*.pxi", "**/*.h", "**/*.pyi"],
            "cypy": ["**/*.pxd", "**/*.pxi", "**/*.pyi"],
        },
        ext_modules=cythonized_extensions,
    )
