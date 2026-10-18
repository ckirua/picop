"""Focused native UUID entropy contract tests."""

from __future__ import annotations

import os
from pathlib import Path
import shlex
import subprocess
import sys
import sysconfig

import pytest

from picop.uuid import _uuid_native


UUID_DIR = Path(_uuid_native.__file__).parent


def _compile(tmp_path: Path, source: str, *defines: str) -> Path:
    harness = tmp_path / "harness.c"
    harness.write_text(source)
    executable = tmp_path / "harness"
    compiler = shlex.split(os.environ.get("CC") or sysconfig.get_config_var("CC") or "cc")
    subprocess.run(
        [*compiler, "-std=c11", "-I", str(UUID_DIR), *defines, str(harness),
         str(UUID_DIR / "uuid.c"), "-lcrypto", "-pthread", "-o", str(executable)],
        check=True, capture_output=True, text=True, timeout=30,
    )
    return executable


def test_buffer_size_requires_minimum_uuid_and_accepts_sixteen(tmp_path: Path) -> None:
    compiler = shlex.split(os.environ.get("CC") or sysconfig.get_config_var("CC") or "cc")
    source = tmp_path / "size.c"
    source.write_text('#include "uuid.h"\nint main(void) { return 0; }\n')
    for size in (0, 1):
        result = subprocess.run(
            [*compiler, "-std=c11", "-I", str(UUID_DIR), f"-DUUID_RANDOM_BUFFER_SIZE={size}",
             str(source), "-c", "-o", str(tmp_path / f"bad-{size}.o")],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode != 0
    subprocess.run(
        [*compiler, "-std=c11", "-I", str(UUID_DIR), "-DUUID_RANDOM_BUFFER_SIZE=16",
         str(source), "-c", "-o", str(tmp_path / "valid.o")],
        check=True, capture_output=True, text=True, timeout=30,
    )


@pytest.mark.skipif(sys.platform != "linux", reason="fault injection uses ELF LD_PRELOAD")
def test_fork_registration_failure_rejects_module_import(tmp_path: Path) -> None:
    source = tmp_path / "atfork_failure.c"
    source.write_text("""
#include <errno.h>
int pthread_atfork(void (*prepare)(void), void (*parent)(void), void (*child)(void)) {
    (void)prepare; (void)parent; (void)child;
    return ENOMEM;
}
int __register_atfork(void (*prepare)(void), void (*parent)(void),
                      void (*child)(void), void *handle) {
    (void)handle;
    return pthread_atfork(prepare, parent, child);
}
""")
    library = tmp_path / "atfork_failure.so"
    compiler = shlex.split(os.environ.get("CC") or sysconfig.get_config_var("CC") or "cc")
    subprocess.run(
        [*compiler, "-shared", "-fPIC", str(source), "-o", str(library)],
        check=True, capture_output=True, text=True, timeout=30,
    )
    environment = os.environ.copy()
    environment["LD_PRELOAD"] = str(library) + (
        ":" + environment["LD_PRELOAD"] if environment.get("LD_PRELOAD") else ""
    )
    script = """
try:
    import picop.uuid
except RuntimeError:
    pass
else:
    raise AssertionError("UUID import accepted failed fork-hook registration")
"""
    result = subprocess.run(
        [sys.executable, "-c", script], env=environment,
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr


def test_entropy_failure_does_not_report_success_or_copy_output(tmp_path: Path) -> None:
    shim = tmp_path / "rand_shim.h"
    shim.write_text("int failing_rand(unsigned char *, int);\n#define RAND_bytes failing_rand\n")
    exe = _compile(tmp_path, r'''
#include <stdint.h>
#include "uuid.h"
int failing_rand(unsigned char *buffer, int length) {
    (void)buffer; (void)length; return 0;
}
int main(void) {
    uint8_t output[UUID_SIZE];
    for (unsigned i = 0; i < UUID_SIZE; ++i) output[i] = 0xa5;
    if (c_uuid_init() != 0) return 2;
    if (c_uuid4(output) != 0) return 3;
    for (unsigned i = 0; i < UUID_SIZE; ++i) if (output[i] != 0xa5) return 4;
    return 0;
}
''', "-include", str(shim))
    subprocess.run([str(exe)], check=True, timeout=10)
