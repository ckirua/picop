import os

from picobuild import Extension, cythonize, find_packages, setup

# Portable by default for redistributable wheels/sdists.
# Set CPY_NATIVE=1 for local benches that want -march=native.
# MSVC has no -Wno-* flags and no -march=native, so its args are kept minimal.
# /std:c11 is required for <stdatomic.h> and _Atomic (cyatomic shim).
if os.name == "nt":
    _compile_args = ["/std:c11", "-O2", "-utf-8"]
else:
    _compile_args = [
        "-O3",
        "-Wno-unused-function",
        "-Wno-unused-variable",
    ]
if os.environ.get("CPY_NATIVE", "").strip() in ("1", "true", "yes") and os.name != "nt":
    _compile_args.insert(1, "-march=native")

# Cython extensions use picop; no cypy compatibility package is built.
cythonized_extensions = cythonize(
    [
        Extension(
            "picop.uuid._uuid_native",
            ["src/picop/uuid/_uuid_native.c"],
            include_dirs=["src/picop/uuid"],
            # MSVC does not understand `-std=c11`; uuid.h asserts portably.
            extra_compile_args=(["-std=c11"] if os.name != "nt" else []) + _compile_args,
            language="c",
        ),
        Extension(
            "picop.uuid._uuid",
            [
                "src/picop/uuid/_uuid.pyx",
                "src/picop/uuid/uuid.c",
                "src/picop/uuid/entropy.c",
            ],
            include_dirs=["src/picop/uuid"],
            extra_compile_args=_compile_args,
            libraries=["bcrypt"] if os.name == "nt" else [],
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
        },
        ext_modules=cythonized_extensions,
    )
